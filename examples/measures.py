from sonarqube.api import SonarQube

sq = SonarQube()

measures = sq.get_measures(component='uk.nhs.nhsbsa.filetransformation:file-transformation-server:release', metricKeys=['ncloc'])
print(measures)

