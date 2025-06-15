
IOP=[250, 300, 350, 400, 450, 500, 600, 696.8, 798.8, 898, 998.4, 1049.4, 1199, 1397, 1597.6, 1800.6, 2000, 2200, 2500, 2800, 3000]


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