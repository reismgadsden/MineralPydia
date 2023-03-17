:: batch script just to improve qol

:: disable echo of course
@ECHO OFF


:: clears all log files
IF "%1"=="-c" (
    break>MetalPydiaCrawl.log
    break>MetalPydiaImageWrangle.log
    GOTO :EOF
)


:: pushes to github with a commit message
IF "%1"=="-p" (
    IF [%2]==[] GOTO COMMITERR ELSE (
        commands -c
        git add .
        git commit -m %2
        git push -u origin main
        ECHO Changes have been pushed
        GOTO :EOF
    )
)

:: runs in sequence
IF "%1"=="-r"(
    python MineralPydiaCrawl.py
    python MineralPydiaImageWrangle.py
    GOTO :EOF
)


:: catches any possible arguement errors
:ARGERR
ECHO A valid flag must be provided
ECHO Valid Flags:
ECHO    -c: Clears log files
ECHO    -p "<commit message>": Pushes to main branch as long as commit message is also provided
GOTO :EOF


:: catches a lack of commit message
:COMMITERR
ECHO A commit message must be given.
GOTO :EOF
