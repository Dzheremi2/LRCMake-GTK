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

gnome.compile_resources(
  'lrcmake-gtk',
  configure_file(
    input: 'lrcmake-gtk.gresource.xml.in',
    output: 'lrcmake-gtk.gresource.xml',
    configuration: conf
  ),
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: blueprints
)

desktop_file = i18n.merge_file(
        input: 'io.github.dzheremi2.lrcmake-gtk.desktop.in',
       output: 'io.github.dzheremi2.lrcmake-gtk.desktop',
         type: 'desktop',
       po_dir: '../po',
      install: true,
  install_dir: get_option('datadir') / 'applications'
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils, args: [desktop_file])
endif

appstream_file = i18n.merge_file(
        input: 'io.github.dzheremi2.lrcmake-gtk.metainfo.xml.in',
       output: 'io.github.dzheremi2.lrcmake-gtk.metainfo.xml',
       po_dir: '../po',
      install: true,
  install_dir: get_option('datadir') / 'metainfo'
)

appstreamcli = find_program('appstreamcli', required: false, disabler: true)
test('Validate appstream file', appstreamcli,
     args: ['validate', '--no-net', '--explain', appstream_file])

install_data('io.github.dzheremi2.lrcmake-gtk.gschema.xml',
  install_dir: get_option('datadir') / 'glib-2.0' / 'schemas'
)

compile_schemas = find_program('glib-compile-schemas', required: false, disabler: true)
test('Validate schema file',
     compile_schemas,
     args: ['--strict', '--dry-run', meson.current_source_dir()])


service_conf = configuration_data()
service_conf.set('bindir', get_option('prefix') / get_option('bindir'))
configure_file(
  input: 'io.github.dzheremi2.lrcmake-gtk.service.in',
  output: 'io.github.dzheremi2.lrcmake-gtk.service',
  configuration: service_conf,
  install_dir: get_option('datadir') / 'dbus-1' / 'services'
)

subdir('icons')
