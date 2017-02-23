"""Overwatch wem extractor v0.3"""
import os
import subprocess
import shutil
import hashlib
import csv
import sys
import json

print("Overwatch wem extractor v0.2")
# get CONFIG
with open("CONFIG.json") as DATA_FILE:
    CONFIG = json.load(DATA_FILE)
COUNTER = 1
UNKNOWN = 0

# get HASH storage
HASHSTORAGE = dict([])
with open(CONFIG["paths"]["important"], "r") as CSVFILE:
    HASHREADER = csv.reader(CSVFILE, delimiter=",")
    for ROW in HASHREADER:
        HASHSTORAGE[ROW[0]] = ROW[1]
with open(CONFIG["paths"]["noise"], "r") as CSVFILE:
    HASHREADER = csv.reader(CSVFILE, delimiter=",")
    for ROW in HASHREADER:
        HASHSTORAGE[ROW[0]] = ROW[1]

# clear unknowns file
open(CONFIG["paths"]["unknowns"], "a").truncate()

FOLDER = CONFIG["paths"]["casc"]

# run through the casc FOLDER
for DIR in os.listdir(FOLDER):
    for FILE in os.listdir(FOLDER + "/" + DIR):
        # grab all the files
        if FILE.endswith(".xxx"):
            PATH = FOLDER + "/" + DIR + "/" + FILE
            with open(PATH, "r") as FILE_DESCRIPTOR:
                # if first line contains wave headers
                FIRST_LINE = FILE_DESCRIPTOR.readline()
                if "WAVEfmt" in FIRST_LINE[:20]:
                    # show some progress
                    if COUNTER % 100 == 0:
                        print(COUNTER)
                    COUNTER = COUNTER + 1
                    # convert to ogg
                    FNULL = open(os.devnull, "w")
                    subprocess.call([CONFIG["paths"]["tools"], "ww2ogg.exe", PATH, "--pcb", CONFIG["paths"]["tools"], "packed_codebooks_aoTuV_603.bin"], stdout=FNULL, stderr=subprocess.STDOUT)
                    # if convert was successful
                    if os.path.isfile(PATH.replace(".xxx", ".ogg")):
                        TEMP_PATH = CONFIG["paths"]["exported"]+str(COUNTER)+".ogg"
                        shutil.move(PATH.replace(".xxx", ".ogg"), TEMP_PATH)
                        # fix ogg
                        subprocess.call([CONFIG["paths"]["tools"], "revorb.exe ", TEMP_PATH], stdout=FNULL, stderr=subprocess.STDOUT)
                        # check against HASH storage
                        HASH = hashlib.md5(TEMP_PATH).hexdigest()
                        if HASH in HASHSTORAGE:
                            # move to a nice FOLDER
                            shutil.move(TEMP_PATH, CONFIG["paths"]["exported"]+HASHSTORAGE[HASH])
                        else:
                            # add HASH to the unknowns list
                            UNKNOWN = UNKNOWN + 1
                            if not CONFIG["full_extract"] and UNKNOWN == 1000:
                                sys.exit("1k unknowns listed. Please proceed to categorize. Ty! <3")
                            LOG = open(CONFIG["paths"]["unknowns"], "a")
                            LOG.write(HASH + "," + TEMP_PATH.replace(CONFIG["paths"]["exported"], "") + "\n")
LOG.close()
