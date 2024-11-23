pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'lrcmake'
gnome = import('gnome')

configure_file(
  input: 'lrcmake.in',
  output: 'lrcmake',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)

install_data(
    [
    '__init__.py',
    'main.py',
    'window.py',
    'components/noDirSelectedGreeting.py',
    'methods/selectData.py',
    'components/songCard.py',
    'methods/parsers.py',
    'components/fileDetails.py',
    'components/syncLine.py',
    'methods/exportData.py',
    'methods/publish.py',
    configure_file(input: 'shared.py.in', output: 'shared.py', configuration: conf),
  ],
  install_dir: moduledir,
)
