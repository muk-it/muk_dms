# MuK Document Management System - Large Object Extension

This module extends MuK Documents to use large objects to store and load files.
        
I case you want to change the save type of an existing Root Setting be aware that this
can trigger a heavy migration process, depending on how many files are currently stored.

Before you start the migration process make sure the following conditions are met:
* no one else is using the system at the time of migration
* no files are locked either by the system or users