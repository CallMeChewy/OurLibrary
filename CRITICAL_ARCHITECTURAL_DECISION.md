# CRITICAL ARCHITECTURAL DECISION - DO NOT CHANGE

## THE PROBLEM WE'VE BEEN FIXING FOR HOURS:

**WRONG APPROACH**: Using File System Access API with `showDirectoryPicker()` 
- This asks users to choose directory location
- Creates confusing popup dialogs  
- Users don't know where to navigate
- This is NOT what we want

**RIGHT APPROACH**: Automatic directory creation
- System automatically creates ~/OurLibrary/ 
- No user dialogs or permission requests
- Tell user where files were placed
- Use downloads API or other automatic methods

## WHAT WE KEEP REVERTING TO (STOP DOING THIS):
- showDirectoryPicker() calls
- Directory selection dialogs
- Asking users where to save files

## WHAT WE ACTUALLY WANT:
- Automatic ~/OurLibrary/ creation
- Real files users can backup/transfer  
- No confusing permission dialogs
- Silent, automatic operation

## USER REQUIREMENT:
"should NOT be asking for location" - files should automatically go to ~/OurLibrary/

This has been the goal for HOURS. Stop reverting to File System Access API!

## CRITICAL TESTING REQUIREMENT:

**NEVER USE LOCAL SERVER FOR TESTING**
- ALWAYS test on live GitHub Pages: https://callmechewy.github.io/OurLibrary/
- Database comes from Google Drive, NOT local files
- User has repeatedly ordered this - NO EXCEPTIONS
- Local testing has caused major disappointments and wasted time

**DATABASE SOURCE**:
- Must use Google Drive direct download link
- NOT local project files
- Google Drive ensures universal access