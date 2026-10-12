import train2, train
def build():
    train2.extra_mats()
    train2.make_tram("tA", seed=3).place(0.0, 0.0, 0.0, z=0.274)
    train2.make_mono("tB", seed=4).place(0.0, 8.0, 0.0, z=0.0)
    train.make_kiha("tC", seed=5).place(0.0, 16.0, 0.0, z=0.274)
