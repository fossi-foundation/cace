# nix/mpld3.nix
{ lib
, buildPythonPackage 
, fetchPypi
, matplotlib
, jinja2
}:

buildPythonPackage rec {
  pname = "mpld3";
  version = "0.5.10";
  
  src = fetchPypi {
    inherit pname version;
    sha256 = "1izv73g88zqffabmaq1fhw2l3afr5hkwycwiql2ja8d59x0fny54";
  };

  propagatedBuildInputs = [ 
    matplotlib 
    jinja2 
  ];

  doCheck = false;

  meta = with lib; {
    description = "D3 Viewer for Matplotlib";
    homepage = "http://mpld3.github.com";
    license = licenses.bsd3;
  };
}