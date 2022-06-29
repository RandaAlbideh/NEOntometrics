import os
from threading import local
from django.conf import settings
import pygit2 as Git
from os import path
import logging
import copy, requests
from datetime import datetime
from rest.CalculationHelper import GitHelper, GitUrlParser
from rest.models import Commit, Repository, OntologyFile
from rest.serializers import DBCommitsInRepositorySerializer
from rest.opiHandler import OpiHandler
from rq import job
import django_rq
import rq
import shutil
from django.core.files import File


class CalculationManager:
    """Handles the all preparation before sending the data to the OPI-Endpoint
    """
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
    @staticmethod
    def putInQueue(url: GitUrlParser, reasonerSelected=True, classMetrics=False):
        calculationManager = CalculationManager()
        jobId = GitHelper.serializeJobId(url)
        if(url.repository == ""):
            django_rq.enqueue(calculationManager.ontologyFileWORepo, url, reasonerSelected, job_id=jobId)
        # If no file is given, analyze the whole REPO
        else:
            metrics = django_rq.enqueue(calculationManager.getObjects, repositoryUrl=url.repository,
                                        classMetrics=classMetrics, reasoner=reasonerSelected, job_id=jobId)
        
    

    @django_rq.job
    def ontologyFileWORepo(self, url: GitUrlParser, reasonerSelected: bool):
        """Analyze a single ontology file that is **not** bound to a repository

        Args:
            url (GitHelper.GitUrlParser): The GitHelper object that contains information regarding the ontoloy file source
            reasonerSelected (bool): Depicts if the metrics are calculated using a reasoner or not.
        """
        returnObject = {}
        try:
            getOntologyResponse = requests.get("http://" + url.file, timeout=settings.SINGLEONTOLOGYRETRIEVETIMOUT)
            ontology = getOntologyResponse.text.replace("\n", "")
            returnObject["Size"] =len(getOntologyResponse.content)
        except:
            returnObject["Size"] = 0
            returnObject["ReadingError"] = "Ontology Source not Available"
        opi = OpiHandler()
        
        
        returnObject["reasonerActive"] = reasonerSelected
        if "ontology" in locals():
            try:
                opiMetrics = opi.opiOntologyRequest(
                    ontologyString=ontology, classMetrics=False, ontologySize=returnObject["Size"] , reasoner=reasonerSelected)
                if "GeneralOntologyMetrics" in opiMetrics:
                    opiMetrics.update(opiMetrics.pop("GeneralOntologyMetrics"))
                    returnObject.update(opiMetrics)
                    self.logger.debug("Ontology Analyzed Successfully")
            except IOError:
                # A reading Error occurs, e.g., if an ontology does not conform to a definied ontology standard and cannot be parsed
                self.logger.warning(
                    "Ontology {0} not Readable ".format(url.file))
                
                returnObject["ReadingError"] = "Ontology not Readable"
        
        ontologyFile = OntologyFile.objects.filter(fileName=url.file)
        if not ontologyFile.exists():
            ontologyFile = OntologyFile.objects.create(fileName=url.file)
        else:
            ontologyFile = ontologyFile[0]
        commit = Commit.objects.filter(metricSource=ontologyFile, reasonerActive = reasonerSelected)
        if not commit.exists():
            Commit.objects.create(metricSource = ontologyFile, **returnObject)
        else:
            commit = Commit(metricSource = ontologyFile, **returnObject, pk=commit[0].id).save()
            

    @django_rq.job
    def getObjects(self, repositoryUrl: str,  branch=None, classMetrics=False, reasoner=False) -> dict:
        """Analysis all ontology files in a git Repository

        Args:
            repositoryUrl (string): URL to remote Repository
            objectLocation (string): relative path to targeted ontology file in Repository
            branch (str, optional): selected branch. Defaults to "None".
            classMetrics (bool, optional): Enables the calculation of Class Metrics (Computational Expensive). Defaults to False.

        Returns:
            dict: Evolutional Ontology Metrics
        """
        repo = None
        internalOntologyUrl = "ontologies/" + str(hash(repositoryUrl))
        if Repository.objects.filter(repository = repositoryUrl).exists():
            repository = Repository.objects.get(repository = repositoryUrl)
            shutil.copy(repository.gitRepositoryFile.path, internalOntologyUrl+ "_packed.zip")
            shutil.unpack_archive( internalOntologyUrl + "_packed.zip", internalOntologyUrl)
            repo = Git.Repository(internalOntologyUrl)
            fetching = repo.remotes[0].fetch() # There is always just one remote configured anyway.
            print("Updated Objects: " + str(fetching.total_objects))
        # Creates a folder for the git-Repository based on the hash of the repository URL.
        else:
            if(path.exists(internalOntologyUrl) == False):
                repo = Git.clone_repository("http://" + repositoryUrl,
                                    internalOntologyUrl, checkout_branch=branch)
                self.logger.debug("Repository cloned at " +  internalOntologyUrl + "_packed.tar.gz")
            repository = Repository.objects.create(repository = repositoryUrl)
        
        # This extremly ugly thing down below is necessary to set the head to the latest remote version. Otherwise, the fetch
        # Downloads the data but stays on the old position, thus preventing the crawler to get the new data.
        repo.reset(repo.references.objects[len(repo.references.objects)-1].target, Git.GIT_RESET_HARD)
        
        index = repo.index
        index.read()
        


        # This part is for counting how much ontologies are to be calculated in this repository
        currentJob = rq.job.get_current_job()
        ontologiesToBeAnalyzed = 0
        analyzedOntologies = 0
        for item in index:
            if(item.path.endswith((".ttl", ".owl", ".rdf"))):
                ontologiesToBeAnalyzed += 1
        currentJob.meta = {"analysableOntologies": ontologiesToBeAnalyzed,
                           "analyzedOntologies": analyzedOntologies}
        currentJob.save_meta()
        
        for item in index:
            if(item.path.endswith((".ttl", ".owl", ".rdf"))):
                self.logger.debug("Analyse Ontology: "+item.path)
                logging.debug("Analyse Ontology: "+item.path)
                
                if(reasoner):
                    self.getOntologyMetrics(objectLocation=item.path, classMetrics=classMetrics, repository=repository, reasoner=False, repo=repo)
                    self.getOntologyMetrics(objectLocation=item.path, classMetrics=classMetrics, repository=repository, reasoner=True, repo=repo)

                else:
                    self.getOntologyMetrics(objectLocation=item.path, classMetrics=classMetrics, repository=repository, reasoner=False, repo=repo)

                analyzedOntologies += 1
                currentJob.meta = {
                    "analysableOntologies": ontologiesToBeAnalyzed, "analyzedOntologies": analyzedOntologies}
                currentJob.save_meta()

        repository.wholeRepositoryAnalyzed = True # A marker in the Database that all Files in it have been analyzed.
        
        repo.free() # Unlockes the File so it can be deleted.
        file = shutil.make_archive(internalOntologyUrl+"_packed", "zip", internalOntologyUrl)
        with open(file, "rb") as packed:
            repository.gitRepositoryFile.save(internalOntologyUrl, File(packed))
        shutil.rmtree(internalOntologyUrl, ignore_errors=True)
        os.remove(file)
        return(True)

    def getOntologyMetrics(self, objectLocation: str, classMetrics: bool, reasoner: bool, repository: Repository, repo: Git.Repository) -> dict:
        """Calculates Evolutional Ontology-Metrics for one ontology file and stores them into a database

        Args:
            objectLocation (string): relative path of requested file in Repository
            classMetrics (bool): Enable or Disable calculation of ClassMetrics
            internalOntologyUrl (string): URL to cloned Repository stored locally on the machine
            remoteLocation (string): URL to the originating repository (For documentation purposes in DB)
            branch (string): Branch to work in
            repo (pygit2.Repository): the pygit2 Repository

        Returns:
            dict: Repository with evolutional ontology-Metrics
        """

        # Read the index of the repo for accessing the files
        index = repo.index
        index.read()
        opi = OpiHandler()
        formerObj = None
        commitList = []
        if OntologyFile.objects.filter(fileName = objectLocation, repository=repository).exists():
            ontologyFile = OntologyFile.objects.get(fileName = objectLocation, repository=repository)
            alreadyExistingCommits =  DBCommitsInRepositorySerializer.flattenReponse(DBCommitsInRepositorySerializer(repository).data)
        else:
            ontologyFile = OntologyFile.objects.create(repository = repository, fileName=objectLocation)
            alreadyExistingCommits = {}
        # Iterates through the Repository, finding the relevant Commits based on paths
        
        for reference in repo.listall_reference_objects():
            if reference.type != 1 or reference.shorthand not in repo.branches.remote: # Only analyze non symbolic branches and such that are from the remote orign.
                continue
            print(reference.shorthand)
            repo.checkout(reference)
            for commit in repo.walk(repo.head.target, Git.GIT_SORT_TOPOLOGICAL | Git.GIT_SORT_REVERSE):
                obj = self._getFittingObject(objectLocation, commit.tree)
                if obj != None:
                    if(formerObj != obj):
                        formerObj = obj
                        if(commit not in commitList):
                            commitList.append(commit)

        # Sorting the Commits based on TIME, not on PARENTS, thus making the list ready for further filtering
        commitList.sort(
            key=lambda commit: datetime.fromtimestamp(commit.commit_time))
        formerObj = None
        commitCounter = 0  # The counter is merely for reporting progress.
        for commit in commitList:
            renamedFrom = None
            # The branches are needed a couple of lines later
            branches = repo.branches.with_commit(commit)
            branches = [branch for branch in branches if branch in repo.branches.remote and "HEAD" not in branch]
            if commit.hex in alreadyExistingCommits.keys(): # The branches that are already in the database do not need to be analyzed again 
                if alreadyExistingCommits.get(commit.hex) != branches: # However, the branches can change (due to commits). So we check if we need to adapt the branches.
                    commitDBEntry = Commit.objects.filter(metricSource = ontologyFile, CommitID = commit.hex)
                    if commitDBEntry.exists():
                        commitDBEntry = commitDBEntry[0]
                        commitDBEntry.branch = branches
                        commitDBEntry.save()
                continue

            deltasToPrevious = [delta.delta for delta in repo.diff(a=commit.parents[0], b=commit, cached=False)]
            previousDelta = None
            for delta in deltasToPrevious:
                if(delta.status == Git.GIT_DELTA_RENAMED):
                    if(objectLocation == delta.new_file.path):
                        renamedFrom =  delta.old_file.path
                if (previousDelta != None):
                    # Mostly, the algorithm does not rightfully detect an item as renamed, but as deleted and added again. If both have the same size, we assume a Rename Event.
                    if (previousDelta.status == Git.GIT_DELTA_DELETED and delta.status == Git.GIT_DELTA_ADDED and previousDelta.old_file.size == delta.new_file.size):
                        renamedFrom =  previousDelta.old_file.path
                previousDelta = delta

            # Attach progress reports to the scheduler-database (REDIS)
            commitCounter += 1
            job = rq.job.get_current_job()
            job.meta.update({ 
                "commitsForThisOntology": len(commitList),
                "ananlyzedCommits": commitCounter
            })
            job.save_meta()

            obj = self._getFittingObject(objectLocation, commit.tree)
            if obj != None:
                if(formerObj != obj):     
                    formerObj = obj
                    returnObject = {}
                    # Commit-Metadata 
                    returnObject["CommitTime"] = datetime.fromtimestamp(
                        commit.commit_time)
                    returnObject["CommitID"] = commit.hex    
                    returnObject["CommitMessage"] = commit.message
                    returnObject["AuthorName"] = commit.author.name
                    returnObject["AuthorEmail"] = commit.author.email
                    returnObject["CommitterName"] = commit.committer.name
                    returnObject["CommiterEmail"] = commit.committer.email
                    returnObject["branch"] = branches
                    returnObject["renamedFrom"] = renamedFrom
                    
                    self.logger.debug(
                        "Date: " + str(returnObject["CommitTime"]))
                    self.logger.debug("Commit:" + commit.message)
                    try:
                        opiMetrics = opi.opiOntologyRequest(
                            obj.data, ontologySize=obj.size, classMetrics=classMetrics, reasoner=reasoner)
                        if "GeneralOntologyMetrics" in opiMetrics:
                            opiMetrics.update(opiMetrics.pop("GeneralOntologyMetrics"))
                        returnObject.update(opiMetrics)
                        self.logger.debug("Ontology Analyzed Successfully")
                    except IOError:
                        # A reading Error occurs, e.g., if an ontology does not conform to a definied ontology standard and cannot be parsed
                        self.logger.warning(
                            "Ontology {0} not Readable ".format(obj.name))
                        returnObject["Size"] = obj.size
                        returnObject["ReadingError"] = "Ontology not Readable"
                    if not Commit.objects.filter(metricSource=ontologyFile, CommitID = commit.hex, reasonerActive = reasoner ).exists():
                        Commit.objects.create(metricSource = ontologyFile, **returnObject)



    def downloadSpecificOntologyFile(self, pkCommit: int)->dict:
        """Retrieves a specific file of a specific commit from a repository for download.

        Args:
            pkCommit (int): ID of the Commit in the databse

        Returns:
            dict: Dict with the name of the file as the key and the value is the data.
        """
        if not(Commit.objects.filter(id=pkCommit).exists()):
            return None
        
        commit = Commit.objects.get(id=pkCommit)
        ontology = commit.metricSource
        repository = ontology.repository
        internalOntologyUrl = "ontologies/" + str(hash(commit.CommitID))
        shutil.copy(repository.gitRepositoryFile.path, internalOntologyUrl+ "_packed.zip")
        shutil.unpack_archive( internalOntologyUrl + "_packed.zip", internalOntologyUrl)
        gitRepo = Git.Repository(internalOntologyUrl)
        ontologyFile = self._getFittingObject(ontology.fileName, gitRepo.get(commit.CommitID).tree)
        returnVal = {ontologyFile.name: ontologyFile.data}
        returnVal = copy.deepcopy(returnVal) # Deep copy is needed to be able to remove the ontology files before deletion.
        gitRepo.free()
        shutil.rmtree(internalOntologyUrl, ignore_errors=True)
        return returnVal
        
    def _getFittingObject(self, searchObj, commitTree):
        """Finds specific File in git-commit-Object

        Args:
            searchObj ([type]): relative URL to findable Object
            commit ([type]): Commmit-Tree Object that shall be searched

        Returns:
            Object: Ontology-File
        """

        if type(searchObj) is list:
            searchList = searchObj
        else:
            searchList = searchObj.split("/")
        breadCrumbCounter = 0
        if(len(searchList) > 1):
            for breadCrumb in searchList:
                # Check if its the last element of the BreadCrumb Object
                if(commitTree.__contains__(breadCrumb)):
                    searchList.pop(0)
                    return(self._getFittingObject(searchList, commitTree.__getitem__(breadCrumb)))
                else:
                    return None
        else:
            if(commitTree.__contains__(searchList[0])):
                if(type(commitTree.__getitem__(searchList[0])) is Git.Tree):
                    self._getFittingObject(
                        searchList[0], commitTree.__getitem__(searchList[0]))
                else:
                    return(commitTree.__getitem__(searchList[0]))
