import g4f.Provider
print([p.__name__ for p in g4f.Provider.__providers__ if p.active])
