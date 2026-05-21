# Google-Drive-to-Calibre-Auto-Add
Calibre doesn't work well with Google Drive, so I made a somewhat janky workaround to use for myself. It is now a plugin you can download that is similar to Calibre's inbuilt automatic adding feature but doesn't delete the files of the folder. The external app that scans a folder of your choosing in Google drive and mirrors onto a folder for Calibre to use its auto add feature is still available to use however([go here](https://github.com/Boop3070/Google-Drive-to-Calibre-Auto-Add/edit/main/README.md#if-you-want-to-use-the-external-app-instead-of-the-plugin-maybe-as-just-a-file-mirror-not-specifically-for-calibre-follow-these-steps)). 

<ins> Download Google Drive Desktop from [here](https://dl.google.com/drive-file-stream/GoogleDriveSetup.exe) </ins>

## Using the plugin

Get the plugin [zip file](https://github.com/Boop3070/Google-Drive-to-Calibre-Auto-Add/tree/main/External)

### Go to Calibre -> Preferences -> Advanced -> Plugins -> Local plugin from file
<p float="left">
  <img width="45%" height="45%" alt="image" src="https://github.com/user-attachments/assets/e761b877-efdf-4580-8742-25d2b83e71a3" />
  &nbsp;
  <img width="45%" height="45%" alt="image" src="https://github.com/user-attachments/assets/7f6b71d9-8ba5-4496-be34-c658637d29cf" />
</p>

### Navigate to zip and select it.
<img width="40%" height="40%" alt="image" src="https://github.com/user-attachments/assets/08397db4-54ad-49a0-8662-23b1e4490444" />


### You will then be prompted to restart Calibre to install the plugin fully. After restarting there should be an option on the toolbar that says "GDrive Watcher"

<img width="1920" height="107" alt="image" src="https://github.com/user-attachments/assets/affe7564-4d00-40ea-b41a-e9c432a405a1" />
<br>&nbsp;<br>

### After clicking it the activity log will appear:

<img width="45%" height="45%" alt="image" src="https://github.com/user-attachments/assets/8cfa565e-a9bd-4ebc-a540-db10a4470166" />
<br>&nbsp;<br>

### Navigate to the settings button, then select your google driver folder containing your ebooks, click Ok, then Restart Watcher.

This should now be scanning your google drive folder(and sub-folders) for any updates depending on the interval you set.

Things to know:
  - The first time you run it the plugin will not add anything to Calibre, it will seed all current files and only add when new files are added in the gdrive folder.
  - The log window is a bit buggy when restarting and doesn't resume the logging, however it will still continue to work. If you want to see the logs again just close and reopen the watcher.
  - Future update might have an option to not seed anything the first time around.

## If you want to use the external app instead of the plugin, maybe as just a file mirror not specifically for Calibre, follow these steps.

### Get the .exe from [here](https://github.com/Boop3070/Google-Drive-to-Calibre-Auto-Add/tree/main/External)

### Run GDrive Watcher.exe -> Settings -> select the folders you have designated for it to scan and mirror the files to(the Google Drive folder and Calibre inbox folder respectively).

<img width="45%" height="45%" alt="image" src="https://github.com/user-attachments/assets/9ead8c52-23a8-4e04-a85f-3584fd9cbae7" />

<br>&nbsp;<br>

### Settings, select the G-Drive folder that has your E-books:
<img width="45%" height="45%" alt="image" src="https://github.com/user-attachments/assets/cb50139c-3067-406f-a4e9-8b9d42393a09" vspace="20"/>
<br>&nbsp;<br>

### The first scan will assume you have already downloaded what is currently on the drive and it is in Calibre.
<img width="45%" height="45%" alt="image" src="https://github.com/user-attachments/assets/19f5e0ce-39ae-4434-a569-819c211966de" vspace="20"/>

<br>&nbsp;<br>

After this, any new E-books you put into your google drive folder, or if someone who you have shared the folder with updates it, the watcher will check against its own json file containing all previously seeded files in the Calibre inbox folder and download the books that aren't in it.

### Enabling Calibre Auto Add: Calibre -> Add books -> Dropdown menu -> Control the adding of books

<img width="45%" height="45%" alt="image" src="https://github.com/user-attachments/assets/50dbfb2c-65c2-492c-9442-7e08ef5b5357" vspace="20"/>

### Automatic adding -> Folder icon -> Select inbox folder

<img width="45%" height="45%" alt="image" src="https://github.com/user-attachments/assets/065c5d7d-e7ee-4d3c-a5e3-322d2df87db0" vspace="30"/>


After this is setup Calibre should look at the inbox folder and copy the files to its library. After that it will delete the contents in the inbox that it copied.



The reason for why it's being done this is way is because of that very deletion of files, if the drive is shared with multiple people(like it is for me) then we want to keep them in there. Second, if you just put your library on Google Drive itself, not only is it incredibly slow, the drive is on a FAT system which Calibre does not like as it's very inefficient. So yeah, having a light program mirror the files seemed like the best solution to me. 

It is janky, but it works for me. Might update it in the future. 





###### Code written partially with the help of Claude Sonnet 4.6
