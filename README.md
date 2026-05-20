# Calibre-to-Google-Drive-Auto-Add
Calibre doesn't work well with Google Drive, so I made a somewhat janky workaround to use for myself. Scans a folder of your choosing in Google drive and mirrors onto a folder for Calibre to use its auto add feature.

<ins> Download Google Drive Desktop from [here](https://dl.google.com/drive-file-stream/GoogleDriveSetup.exe) </ins>

### When you open the GDrive Watcher.exe the picure below will pop up, you will need to go to settings first and select the folders you have designated for it to scan and mirror the files to(Google Drive folder and Calibre inbox folder respectively).

<img width="676" height="462" alt="image" src="https://github.com/user-attachments/assets/9ead8c52-23a8-4e04-a85f-3584fd9cbae7" />

<br>&nbsp;<br>

### Settings, select the G-Drive folder that has your E-books:
<img width="802" height="521" alt="image" src="https://github.com/user-attachments/assets/cb50139c-3067-406f-a4e9-8b9d42393a09" vspace="20"/>
<br>&nbsp;<br>

### The first scan will assume you have already downloaded what is currently on the drive and it is in Calibre.
<img width="805" height="457" alt="image" src="https://github.com/user-attachments/assets/19f5e0ce-39ae-4434-a569-819c211966de" vspace="20"/>

<br>&nbsp;<br>

After this, any new E-books you put into your google drive folder, or if someone who you have shared the folder with updates it, the watcher will check against its json file in the Calibre inbox folder and download the books that aren't in it.

### After setting this up, go to Calibre -> Add books -> Dropdown menu -> Control the adding of books

<img width="556" height="348" alt="image" src="https://github.com/user-attachments/assets/50dbfb2c-65c2-492c-9442-7e08ef5b5357" vspace="20"/>
<br>&nbsp;<br>
### Automatic adding -> Folder icon -> Select inbox folder
<img width="1157" height="932" alt="image" src="https://github.com/user-attachments/assets/065c5d7d-e7ee-4d3c-a5e3-322d2df87db0" vspace="30"/>


After this is setup Calibre should look at the inbox folder and copy the files to its library. After that it will delete the contents in the inbox that it copied.



The reason for why it's being done this is way is because of that very deletion of files, if the drive is shared with multiple people(like it is for me) then we want to keep them in there. Second, if you just put your library on Google Drive itself, not only is it incredibly slow, the drive is on a FAT system which Calibre does not like as it's very inefficient. So yeah, having a light program mirror the files seemed like the best solution to me. 

It is janky, but it works for me. Might update it in the future. 





###### Code written partially with the help of Claude Sonnet 4.6
