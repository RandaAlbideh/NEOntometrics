from django.conf import settings
from django.http.request import RAISE_ERROR
from rest.CalculationHelper import GitUrlParser
from rest.models import Metrics, Source, ClassMetrics
from collections import OrderedDict
from rest.serializers import MetricSerializer, _MetricDetailSerializer
from django.db.models import Q
import logging, django_filters


class DBHandler:
    """Handles the Database connections, especially prepares the metrics for writing into the database.
    """

    def _flattenCommitStructure(self, commitMetrics: dict) -> dict:
        """Flattens the nested Dict-Metrics to prepare it for a database write.

        Args:
            commitMetrics (dict): Calculated Ontology Metrics in nested structure

        Returns:
            dict: flattend Dict prepared for DB-write
        """
        tmpDict = {}
        tmpDict["CommitTime"] = commitMetrics["CommitTime"]
        tmpDict["CommitMessage"] = commitMetrics["CommitMessage"]
        tmpDict["AuthorName"] = commitMetrics["AuthorName"]
        tmpDict["AuthorEmail"] = commitMetrics["AuthorEmail"]
        tmpDict["CommitterName"] = commitMetrics["CommitterName"]
        tmpDict["CommiterEmail"] = commitMetrics["CommiterEmail"]
        tmpDict["ReadingError"] = commitMetrics["ReadingError"]
        tmpDict["CommitID"] = commitMetrics["CommitID"]
        tmpDict["Size"] = commitMetrics["Size"]
        if "GeneralOntologyMetrics" in commitMetrics:
            tmpDict.update(
                commitMetrics["GeneralOntologyMetrics"])
        return tmpDict

    def writeInDB(self, metricsDict: dict, file: str, repo: str, wholeRepo=False, branch: str = "") -> Source:
        """Writes calculated metric-Values in Database

        Args:
            metricsDict (dict): Dictionary containing the metric-values
            branch (str): analzed banch
            file (str): Relative path to ontology within repository
            repo (str): Repository URL
            wholeRepo(bool): Stores if the whole repository was analyzed or not
        """
        if(branch == None):
            branch = ""      
                 
        sourceModel = Source.objects.create(
            fileName=file, repository=repo, branch=branch, wholeRepositoryAnalyzed=wholeRepo)
        for commitMetrics in metricsDict:
            # This statement is a little bit "rough". However, if the iteration on metricsDict is a string,
            # then we analyzed a single ontology metric (then have not analyzed a Repository) and do not need to run the "@commit2Metrics" method.
            if(type(commitMetrics) == str):
                metricsModel = Metrics.objects.create(metricSource=sourceModel)
                modelDict = metricsDict["OntologyMetrics"]["GeneralOntologyMetrics"]
                modelDict.update(
                    {"Size": metricsDict["Size"], "ReadingError": metricsDict["ReadingError"]})
                metricsModel.__dict__.update(modelDict)
                metricsModel.save()
                break
            else:
                metricsModel = Metrics.objects.create(
                    CommitTime=commitMetrics["CommitTime"], metricSource=sourceModel)
                modelDict = self._flattenCommitStructure(commitMetrics)
                metricsModel.__dict__.update(modelDict)
                metricsModel.save()
        return sourceModel

    #@DeprecationWarning
    def getMetricForOntology(self, repository: str, file="", reasonerSelected: bool = False, branch="", classMetrics=False, hideId=True) -> dict:
        """Retrieves Metric Calculation (for one ontology or whole Repo) from the database. 

        Args:
            repository (str): URL to Repository and service (e.g. github.com/ESIPFed/sweet/).
            file (str, optional): URL to the target file within the repository (e.g. src/human.ttl). Defaults to "". If left empty, the whole repo will be analysed
            branch (str, optional): branch to analyse. Defaults to "master".
            classMetrics (bool, optional): If the class-metrics shall be retrieved as well. Defaults to False.
            hideId(bool, optional): Hides the ID of the Database Entry for further identification

        Raises:
            Exception: Inconsistend Data in the DB
        Returns:
            dict: Array with the metrics. If no Metrics are found, the method returns an empty Dict {}
        """

        if(file == ""):
            sourceData = Source.objects.filter(
                repository=repository, wholeRepositoryAnalyzed=1)
        else:
            sourceData = Source.objects.filter(
                repository=repository, fileName=file, branch=branch)
        if file != "" and len(sourceData.values()) > 1:
            logging.critical(
                "More than one Calculation for an Ontology already in the DB")
            raise Exception("To much fitting Data in DB")
        elif len(sourceData.values()) == 0:
            return {}
        metricsArray = []
        iterator = 0
        for SourceRepo in sourceData:
            returnDict = OrderedDict()
            metricsDict = OrderedDict()
            # If the size is larger than the reasoning limit, the reasoner will always be false.
            # Thus, querying with the input parameter will just return empty values. This complex query
            # avoids this problem and returns also metrics with deactivated reasoner.
            metricsLargerThanReasoningLimit = Q(
                Size__gt=settings.REASONINGLIMIT) & Q(reasonerActive__exact=False)
            metricsSmallerThanReasoningLimit = Q(Size__lte=settings.REASONINGLIMIT) & Q(
                reasonerActive__exact=reasonerSelected)
            metricsAssociatedWithOntology = Q(metricSource=SourceRepo)
            metricsData = Metrics.objects.filter(metricsAssociatedWithOntology & (
                metricsLargerThanReasoningLimit | metricsSmallerThanReasoningLimit))
            #metricsData = Metrics.objects.filter(metricSource=SourceRepo, reasonerActive =reasonerSelected)
            queryMetaData = sourceData.values()[iterator]
            iterator += 1
            if hideId:
                queryMetaData.pop("id")
            returnDict.update(queryMetaData)
            metricsDataToDict = []
            for commitMetrics in metricsData.values():
                data = OrderedDict()
                # This ugly piece of code stores the first items in the dict (without db's foreign/primary keys )
                data.update(OrderedDict(list(commitMetrics.items())))
                if(classMetrics):
                    classMetricList = []
                    for classMetric in ClassMetrics.objects.filter(metric=commitMetrics["id"]).values():
                        if hideId:
                            classMetric.pop("metric_id")
                            classMetric.pop("id")
                        classMetricList.append(classMetric)

                        # If no Classmetrics where found but were requested, return 0 (and trigger new calculation)
                    if(len(classMetricList) < 1):
                        return None
                    data.update({"Classmetrics": classMetricList})
                metricsDataToDict.append(data)
            returnDict.update({"metrics": metricsDataToDict})
            metricsArray.append(returnDict)

        return metricsArray

    def deleteMetric(self, repository: str, file=""):
        """Deletes the metrics from the DB

        Args:
            repository (str): URL to Repository and service (e.g. github.com/ESIPFed/sweet/).
            file (str, optional): URL to the target file within the repository (e.g. src/human.ttl). Defaults to "". If left empty, the whole repo will be deleted
        """
        if(file == ""):
            Source.objects.filter(repository=repository).delete()
        else:
            Source.objects.filter(repository=repository,
                                  fileName=file).delete()
            Source.objects.filter(repository=repository).update(
                wholeRepositoryAnalyzed=False)

    def setWholeRepoAnalyzed(self, repository: str):
        """Marks that all files in a repository are analyzed

        Args:
            repository (str): url to Repository
        """
        repoMetrics = Source.objects.filter(repository=repository)
        repoMetrics.update(wholeRepositoryAnalyzed=True)


class RepositoryFilter(django_filters.FilterSet):
    """A custom django-repository filter. Filters the Repository for the filenames and Repository names that are part of a git-url

    Args:
        django_filters (_type_): 

    Returns:
        django_filter.queryset.filter: A django-filter set for filtering django Models
"""
    repository = django_filters.CharFilter(field_name="repository", method="repoFilter", required=True)
    fileName = django_filters.CharFilter(field_name="fileName", method="fileFilter")
    

    def repoFilter(self, queryset, name, value):
        urlObject = GitUrlParser()
        urlObject.parse(value)
        return queryset.filter(repository = urlObject.repository)
        
    def fileFilter(self, queryset, name, value):
        urlObject = GitUrlParser()
        urlObject.parse(value)
        return queryset.filter(fileName = urlObject.file)