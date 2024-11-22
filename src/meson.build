pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'lrcmake'
gnome = import('gnome')

blueprints = custom_target('blueprints',
  input: files(
    'gtk/window.blp',
    'gtk/components/noDirSelectedGreeting.blp',
    'gtk/components/songCard.blp',
    'gtk/components/fileDetails.blp',
    'gtk/components/syncLine.blp',
    'gtk/help-overlay.blp',
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources('lrcmake',
  'lrcmake.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: blueprints,
)

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
