{
  stdenvNoCC,
}:
stdenvNoCC.mkDerivation {
  pname = "driverbrainz";
  version = "0.1.0";

  src = ./.;

  installPhase = ''
    runHook preInstall
    install -D --mode=0644 --target-directory=$out/bin driverbrainz.py
    runHook postInstall
  '';
}
