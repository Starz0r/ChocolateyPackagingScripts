$WORKDIR = $args[0];
$BRANCH = $args[1];

Set-Location $WORKDIR;

# clone the repository and submodules recursively
git clone https://github.com/MaskRay/ccls --recurse-submodules --recursive --depth=1 -j24 -b $BRANCH --single-branch;
cd ccls;
mkdir build;
cd build;

# download vendored llvm
wget https://ziglang.org/deps/llvm+clang-7.0.0-win64-msvc-release.tar.xz;
7z e -txz "llvm+clang-7.0.0-win64-msvc-release.tar.xz";
7z x "llvm+clang-7.0.0-win64-msvc-release.tar";

# generate files and build
cmd /v:on /c " `"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat`" x64 && cmake .. -BRelease -DCMAKE_BUILD_TYPE=Release -G Ninja -DCMAKE_PREFIX_PATH=$pwd\llvm+clang-7.0.0-win64-msvc-release -DCMAKE_CXX_COMPILER=`"cl.exe`" -DCMAKE_LINKER=`"lld-link`" ";
cd Release;
cmd /v:on /c " `"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat`" x64 && ninja";