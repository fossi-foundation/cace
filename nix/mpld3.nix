{
  lib,
  buildPythonPackage,
  setuptools,
  fetchPypi,
  matplotlib,
  jinja2,
}:

buildPythonPackage rec {
  pname = "mpld3";
  format = "pyproject";
  version = "0.5.10";

  src = fetchPypi {
    inherit pname version;
    sha256 = "1izv73g88zqffabmaq1fhw2l3afr5hkwycwiql2ja8d59x0fny54";
  };

  build-system = [ setuptools ];

  propagatedBuildInputs = [
    matplotlib
    jinja2
  ];

  doCheck = false;

  meta = with lib; {
    description = "D3 Viewer for Matplotlib";
    homepage = "https://github.com/mpld3/mpld3";
    license = licenses.bsd3;
  };
}
