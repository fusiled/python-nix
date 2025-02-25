import nix
pkgs = nix.getenv().nimport(nix.lookup_path("<nixpkgs>"))({'overlays': []})

hello = pkgs.hello
print(repr(hello))

hello2 = pkgs.hello.overrideAttrs(lambda o: {
    "pname": str(o.pname) + "-test",
    "versionCheckPhase": 'echo all good',
    "nativeInstallCheckInputs": []
})
print(repr(hello2))
print(hello2.build())
z2n = nix.getenv().getFlake("github:DeterminateSystems/zero-to-nix")
print(z2n.outputs.apps["x86_64-darwin"].default.type)

class Hello:
    def __init__(self):
        self.x = 42
    def hi(self):
        return self.x

test = nix.expr.ExternalValue(Hello())
print(nix.eval('x: x')(test))
