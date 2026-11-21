{
  firefox,
  geckodriver,
  lib,
  python3Packages,
}:
python3Packages.buildPythonApplication {
  pname = "driverbrainz";
  version = "0.1.0";
  pyproject = false;

  src = lib.fileset.toSource {
    root = ./.;
    fileset = lib.fileset.unions [
      ./driverbrainz.py
      ./parse_wikipedia_chapters.py
      ./pyproject.toml
      ./tests
    ];
  };

  dependencies = with python3Packages; [
    platformdirs
    pykakasi
    requests
    selenium
    wikitextparser
  ];

  installPhase = ''
    runHook preInstall
    install -D --mode=0755 driverbrainz.py $out/bin/driverbrainz
    install -D --mode=0755 parse_wikipedia_chapters.py $out/bin/parse-wikipedia-chapters
    runHook postInstall
  '';

  makeWrapperArgs = [
    "--prefix PATH : ${
      lib.makeBinPath [
        firefox
        geckodriver
      ]
    }"
  ];

  nativeCheckInputs = [ python3Packages.pytestCheckHook ];

  # driverbrainz creates its cache directory when imported.
  preCheck = ''
    export HOME="$(mktemp -d)"
  '';

  meta = {
    description = "Automate time-consuming tasks contributing metadata to BookBrainz and MusicBrainz";
    homepage = "https://github.com/jwillikers/driverbrainz";
    license = lib.licenses.gpl3Only;
    mainProgram = "driverbrainz";
  };
}
