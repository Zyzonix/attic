#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 08-06-2023 13:04:10
# 
# file          | repo-helper/sync-repo-from-github.py
# project       | repo-helper
# file version  | 0.0.0
#

#
# Description: source deb packges from github releases
# -> run this daily to be always up to date (via crontab)
#

from datetime import datetime
from configparser import ConfigParser
import os
import traceback
import subprocess
import wget
import shutil

# static config
configFile = "sync-repo-from-github.ini"
# configFile = "/root/repo-helper/sync-repo-from-github.ini"
configFileGeneral = "GENERAL"


# time for logging / console out
class time():
    def getTime():
        curTime = "" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        return curTime


# message handling (logging/console out)
class logging():

    # delete old logfiles, only keep last month
    def logFileCleanUp(self):
        for file in os.listdir(self.logFileDir):
            filename = file.split(".")[0]
            fileNameContents = filename.split("-")
            if (int(fileNameContents[0]) < int(datetime.now().strftime("%Y"))) or (int(fileNameContents[1]) < (int(datetime.now().strftime("%m")) - 1)):
                os.remove(self.logFileDir + file)

    def toFile(self, msg):
        if not (os.path.isdir(self.logFileDir)): os.system("mkdir -p " + self.logFileDir)
        logFile = open(self.logFileDir + str(datetime.now().strftime("%Y-%m")) + ".log", "a")
        logFile.write(msg + "\n")
        logFile.close()
        logging.logFileCleanUp(self)

    def write(self, msg):
        message = str(time.getTime() + " INFO   | " + str(msg))
        print(message)
        logging.toFile(self, message)

    def writeError(self, msg):
        message = str(time.getTime() + " ERROR  | " + msg)
        print(message)
        logging.toFile(self, message)

    # log/print error stack trace
    def writeExecError(self, msg):
        message = str(msg)
        print(message)
        logging.toFile(self, message)

    def writeFailed(self, msg):
        message = str(time.getTime() + " FAILED | " + msg)
        print(message)
        logging.toFile(self, message)

    def writeSubprocessout(self, msg):
        for line in msg:
            line = str(line)
            line = line[:-3]
            line = line[3:]
            logging.write(self, "SYS   | " + line)


class core():

    # get repositories from file and split them to list
    def getRepositories(self):
        repositoriesFromFile = self.cnfgImp[configFileGeneral]["remote_sources"]
        repositoriesFromFileSplit = []

        try:
            repositoriesFromFileSplit = repositoriesFromFile.split(",")
        except:
            logging.write(self, "Failed to split imported repositories")
            logging.writeExecError(self, traceback.format_exc())
            return
        
        return repositoriesFromFileSplit

    # finally update ini file
    def updateConfig(self):
        logging.write(self, "Updating config file")
        self.cnfgImp[configFileGeneral]["last_update"] = str(time.getTime())
        try:
            configFileChange = open(configFile, "w")
            self.cnfgImp.write(configFileChange)
        except:
            logging.writeFailed(self, "Updating config file failed")
            logging.writeExecError(self, traceback.format_exc())
            return False

    # remove unwanted letters from version
    def editVersion(self, version):
        if "-" in version:
            return version.rsplit("-", 1)[0]
        return version

    # edit name of file / add architecture if not in
    def renameFile(self, file, architecture):
        try:
            if not architecture in file:
                fileNameNew = file.replace(".deb", "_" + architecture + ".deb")
                os.rename(self.downloads + file, self.downloads + fileNameNew)
        except:
            logging.writeError(self, "Failed to move all downloads to repository's directory")
            logging.writeExecError(self, traceback.format_exc())

    # move all files to correct dir
    def fileHandler(self):
        filesToMove = os.listdir(self.downloads)
        if filesToMove: logging.write(self, "Moving downloaded files to final repository directory (" + self.finalDebDir + ")")
        try: 
            for file in filesToMove:
                shutil.move(self.downloads + file, self.finalDebDir + file)
        except:
            logging.writeError(self, "Failed to move all downloads to repository's directory")
            logging.writeExecError(self, traceback.format_exc())
            return False

    # update downloaded version in ini file
    def updateVersion(self, repository, version, oldversion):
        logging.write(self, "Updating version in config for " + repository + " from " + oldversion + " to " + version)
        self.cnfgImp[repository.upper()]["version"] = version
        #print(self.cnfgImp[repository.upper()]["version"])

    # get full repository name from config
    def getFullRepositoryName(self, repository):
        fullRepositoryName = self.cnfgImp[repository.upper()]["repo_name"]
        return fullRepositoryName

    def getCurrentReleaseFromFile(self, repository):
        try:
            currentRelease = self.cnfgImp[repository.upper()]["version"]
        except:
            logging.writeFailed(self, "Failed to get current version for " + repository + " - check 'version' in your config")
            logging.writeExecError(self, traceback.format_exc())
            return
        return currentRelease

    # look for latest release on github
    def getLatestRelease(self, repository):
        try:
            fullRepositoryName = self.getFullRepositoryName(repository)
        except:
            logging.writeFailed(self, "Failed to get full repository name from file - check your config at " + repository + " 'repo_name'")
            logging.writeExecError(self, traceback.format_exc())
            return
    
        try: 
            getLatestVersionCommand = "curl https://api.github.com/repos/" + fullRepositoryName + "/releases/latest -s | grep 'tag_name' | awk '{print substr($2, 2, length($2)-3) }'"
            latestVersionEncoded = subprocess.run(getLatestVersionCommand, capture_output=True, shell=True)
            # decode and remove last \n 
            latestVersion = latestVersionEncoded.stdout.decode()[:-1]
            #latestVersion = self.getCurrentReleaseFromFile(repository)
            if not latestVersion: 
                logging.writeFailed(self, "Was not able to retrieve latest version for " + repository)
                return False
            return latestVersion
        
        except:
            logging.writeError(self, "Failed to get full repository name from file - check your config at " + repository + " 'repo_name'")
            logging.writeExecError(self, traceback.format_exc())
            return False


    # download latest release files
    def downloadHandler(self, repository, version, oldversion):
        # get architectures
        try:
            architectures = self.cnfgImp[repository.upper()]["architectures"].split(",")
            packages = self.cnfgImp[repository.upper()]["packages"].split(",")
        except:
            logging.writeFailed(self, "Failed to get architectures from file - check your config at " + repository + " 'repo_name'")
            logging.writeExecError(self, traceback.format_exc())
            return False
        
        # edit version to download-compatible version, if release is 1.1.7-7 but download 1.1.7
        downloadVersion = self.editVersion(version) 

        # get naming schemes from file
        for architecture in architectures:
            nameSchemeFromFile = self.cnfgImp[repository.upper()]["name_scheme_" + architecture]
            
            # iterate through packages 
            for package in packages:
                finalPackage = nameSchemeFromFile.replace("?PACKAGE?", package).replace("?VERSION?", downloadVersion)
                
                # download file
                urlToDownload = "https://github.com/" + self.cnfgImp[repository.upper()]["repo_name"] + "/releases/download/" + version + "/" + finalPackage
                try: 
                    wget.download(urlToDownload, self.downloads + finalPackage)
                    # print empty line 
                    print()
                    logging.write(self, "Downloaded " + finalPackage + " successfully")
                except:
                    logging.writeError(self, "Failed to download " + finalPackage)
                    logging.writeExecError(self, traceback.format_exc())
                    return
                try: self.renameFile(finalPackage, architecture)
                except: 
                    logging.writeError(self, "Could not rename files")
                    logging.writeExecError(self, traceback.format_exc())
                try: self.updateVersion(repository, version, oldversion)
                except: 
                    logging.writeError(self, "Could not update version in config file")
                    logging.writeExecError(self, traceback.format_exc())

    # main process handler
    def runner(self):

        # try importing repos from file
        try:
            repositoriesToSync = self.getRepositories()
        except:
            logging.writeError(self, "Failed to import repositories to sync from file")
            logging.writeExecError(self, traceback.format_exc())
            return
        
        for repository in repositoriesToSync:
            logging.write(self, "Trying to sync " + repository)
            
            # get latest release
            lastestRelease = self.getLatestRelease(repository)
            
            # check if remote latest version is locally available
            localCurrentRelease = self.getCurrentReleaseFromFile(repository)
            
            # if local and remote version are equal -> lookup next
            if not localCurrentRelease == lastestRelease:
                if not ("beta" or "alpha") in lastestRelease: 
                    logging.write(self, "Update available for " + repository)
                    self.downloadHandler(repository, lastestRelease, localCurrentRelease)
                else:
                    logging.write(self, repository + "'s latest release contains alpha/beta - skipping")
            else:
                logging.write(self, "Local version is the newest - skipping " + repository)
                
        # finally move all files and update versions in config
        self.fileHandler()
        self.updateConfig()
            

    def __init__(self):

        # create config importer
        self.cnfgImp = ConfigParser(comment_prefixes='/', allow_no_value=True)
        
        # open config.ini file
        self.cnfgImp.read(configFile)

        try:
            # get logfile path
            self.logFileDir = self.cnfgImp[configFileGeneral]["logfiledir"]
            self.downloads = self.cnfgImp[configFileGeneral]["downloads"]
            self.finalDebDir = self.cnfgImp[configFileGeneral]["final_deb_dir"]
        except:
            print(traceback.format_exc())
            print("ERROR | Wasn't able to read config file")
            print("ERROR | Check your if the path to your config.ini in core.py is correct!")
            return
        
        # start main function
        self.runner()


if __name__ == "__main__":
    core() 
