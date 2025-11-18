new: old: {
  rich = old.rich (finalAttrs: previousAttrs: {
    version = "14.0.0";
  });
  
  # Add mpld3 below the existing rich override
  python3 = old.python3.override {
    packageOverrides = python-self: python-super: {
      mpld3 = python-self.callPackage ./mpld3.nix {};
    };
  };
}