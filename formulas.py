
IOP = [96.8, 111.6, 125, 142.8, 160.8, 178.6, 201, 223.4, 250.4, 314.8, 366, 416.4, 466.8, 518, 619.6, 700, 800, 900,
       1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500]


def find_closest_iop_index_by_formula(discharge):
    velocity = 3
    id_of_pipe = (((4 / (velocity / discharge)) / 3.14)**(1/2)) * 1000
    closest_value = min(IOP, key=lambda x: abs(x-id_of_pipe))
    iop_index = IOP.index(closest_value)
    print("*", IOP[iop_index])
    return iop_index


find_closest_iop_index_by_formula(0.00648)


def find_friction_head_loss_by_formula(length, discharge, cr_value, iop):
    fhl = ((length * (discharge / cr_value) ** 1.81) / (994.62 * (iop / 1000) ** 4.81)) * 1.1
    return round(fhl, 5)


def find_residual_head_at_end_by_formula(diff_in_g_level, rhas, fhl):
    rhae = (diff_in_g_level + rhas) - fhl
    return round(rhae, 5)

def find_velocity_by_formula(discharge, id_of_pipe):
    velocity = discharge * (4 / (3.14 * (id_of_pipe / 1000) ** 2))
    return round(velocity, 5)