import os
import platform
from setuptools import setup

# "import" __version__
__version__ = 'unknown'
for line in open('sounddevice.py'):
    if line.startswith('__version__'):
        exec(line)
        break

MACOSX_VERSIONS = '.'.join([
    'macosx_10_6_x86_64',  # for compatibility with pip < v21
    'macosx_10_6_universal2',
])

# =============================================================================
# DEBUG: Print environment and platform information
# =============================================================================
print("=" * 70)
print("SETUP.PY DEBUG INFORMATION")
print("=" * 70)

# environment variables for cross-platform package creation
system = os.environ.get('PYTHON_SOUNDDEVICE_PLATFORM', platform.system())
machine = platform.machine().lower()
architecture0 = os.environ.get('PYTHON_SOUNDDEVICE_ARCHITECTURE',
    'arm64' if machine in ['arm64', 'aarch64'] else platform.architecture()[0])

print(f"Environment Variables:")
print(f"  PYTHON_SOUNDDEVICE_PLATFORM: {os.environ.get('PYTHON_SOUNDDEVICE_PLATFORM', '<not set>')}")
print(f"  PYTHON_SOUNDDEVICE_ARCHITECTURE: {os.environ.get('PYTHON_SOUNDDEVICE_ARCHITECTURE', '<not set>')}")
print()
print(f"Platform Detection:")
print(f"  platform.system(): {platform.system()}")
print(f"  platform.machine(): {platform.machine()}")
print(f"  platform.machine().lower(): {machine}")
print(f"  platform.architecture(): {platform.architecture()}")
print(f"  platform.architecture()[0]: {platform.architecture()[0]}")
print()
print(f"Resolved Values:")
print(f"  system: {system}")
print(f"  architecture0: {architecture0}")
print()

# =============================================================================

if system == 'Darwin':
    libname = 'libportaudio.dylib'
    print(f"Target: macOS")
    print(f"  Library: {libname}")
elif system == 'Windows':
    libname = 'libportaudio' + architecture0 + '.dll'
    libname_asio = 'libportaudio' + architecture0 + '-asio.dll'
    print(f"Target: Windows")
    print(f"  Library: {libname}")
    print(f"  Library (ASIO): {libname_asio}")
else:
    libname = None
    print(f"Target: {system} (no platform-specific library)")

print()

if libname and os.path.isdir('_sounddevice_data/portaudio-binaries'):
    packages = ['_sounddevice_data']
    package_data = {'_sounddevice_data': ['portaudio-binaries/' + libname,
                                          'portaudio-binaries/README.md']}
    if system == 'Windows':
        package_data['_sounddevice_data'].append(
            'portaudio-binaries/' + libname_asio)
    zip_safe = False
    
    print(f"Package Configuration:")
    print(f"  Packages: {packages}")
    print(f"  Package data: {package_data}")
    print(f"  Zip safe: {zip_safe}")
    
    # Check if the library file actually exists
    lib_path = os.path.join('_sounddevice_data/portaudio-binaries', libname)
    if os.path.exists(lib_path):
        print(f"  ✓ Library file exists: {lib_path}")
    else:
        print(f"  ✗ WARNING: Library file NOT found: {lib_path}")
    
    if system == 'Windows':
        asio_path = os.path.join('_sounddevice_data/portaudio-binaries', libname_asio)
        if os.path.exists(asio_path):
            print(f"  ✓ ASIO library file exists: {asio_path}")
        else:
            print(f"  ✗ WARNING: ASIO library file NOT found: {asio_path}")
else:
    packages = None
    package_data = None
    zip_safe = True
    
    print(f"Package Configuration:")
    print(f"  No platform-specific packages (pure Python wheel)")
    if libname:
        print(f"  Reason: Directory '_sounddevice_data/portaudio-binaries' not found")

print()

try:
    from wheel.bdist_wheel import bdist_wheel
except ImportError:
    cmdclass = {}
    print(f"Wheel Command Class: <not available>")
else:
    class bdist_wheel_half_pure(bdist_wheel):
        """Create OS-dependent, but Python-independent wheels."""
        def get_tag(self):
            if system == 'Darwin':
                oses = MACOSX_VERSIONS
            elif system == 'Windows':
                if architecture0 == 'arm64':
                    oses = 'win_arm64'
                elif architecture0 == '32bit':
                    oses = 'win32'
                else:
                    oses = 'win_amd64'
            else:
                oses = 'any'
            
            print(f"Wheel Tag Generation:")
            print(f"  Python: py3")
            print(f"  ABI: none")
            print(f"  Platform: {oses}")
            
            return 'py3', 'none', oses
    
    cmdclass = {'bdist_wheel': bdist_wheel_half_pure}
    print(f"Wheel Command Class: bdist_wheel_half_pure")

print("=" * 70)
print()

setup(
    name='sounddevice',
    version=__version__,
    py_modules=['sounddevice'],
    packages=packages,
    package_data=package_data,
    zip_safe=zip_safe,
    python_requires='>=3.7',
    setup_requires=['CFFI>=1.0'],
    install_requires=['CFFI>=1.0'],
    extras_require={'NumPy': ['NumPy']},
    cffi_modules=['sounddevice_build.py:ffibuilder'],
    author='Matthias Geier',
    author_email='Matthias.Geier@gmail.com',
    description='Play and Record Sound with Python',
    long_description=open('README.rst').read(),
    license='MIT',
    keywords='sound audio PortAudio play record playrec'.split(),
    url='http://python-sounddevice.readthedocs.io/',
    project_urls={
        'Source': 'https://github.com/spatialaudio/python-sounddevice',
    },
    platforms='any',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Sound/Audio',
    ],
    cmdclass=cmdclass,
)
