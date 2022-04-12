@echo off

if not exist msvc md msvc
if exist msvc\CMakeCache.txt del msvc\CMakeCache.txt

FOR /F "tokens=* USEBACKQ" %%F IN (`git describe --always`) DO ( SET git_describe=%%F )
echo GIT TOKENS = %git_describe%

cd msvc
cmake -DCMAKE_INSTALL_PREFIX=../deploy/%git_describe% -G "Visual Studio 16 2019" -A x64 ../
cd ..
