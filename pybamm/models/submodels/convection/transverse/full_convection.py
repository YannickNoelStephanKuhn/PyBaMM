#
# Submodel for pressure driven convection in transverse directions
#
import pybamm
from .base_transverse_convection import BaseTransverseModel


class Full(BaseTransverseModel):
    """
    Submodel for the full model of pressure-driven convection in transverse directions

    Parameters
    ----------
    param : parameter class
        The parameters to use for this submodel

    **Extends:** :class:`pybamm.convection.through_cell.BaseTransverseModel`
    """

    def __init__(self, param):
        super().__init__(param)

    def get_fundamental_variables(self):

        p_s = pybamm.Variable("Separator pressure", domain="current collector")
        variables = self._get_standard_separator_pressure_variables(p_s)

        # TODO: put in permeability and viscosity
        Vbox_s = -pybamm.grad(p_s)
        variables.update(
            self._get_standard_transverse_velocity_variables(Vbox_s, "velocity")
        )

        div_Vbox_s = pybamm.div(Vbox_s)
        variables.update(
            self._get_standard_transverse_velocity_variables(div_Vbox_s, "acceleration")
        )

        return variables

    def set_algebraic(self, variables):
        p_s = variables["X-averaged separator pressure"]
        div_Vbox_s = self._get_separator_velocity(variables)
        Vbox_s = variables["X-averaged separator transverse volume-averaged velocity"]

        # Problem in the z-direction for p_s
        self.algebraic = {p_s: pybamm.div(Vbox_s) - div_Vbox_s}

    def set_boundary_conditions(self, variables):
        p_s = variables["X-averaged separator pressure"]

        # Boundary conditions in z-direction for p_s (left=bottom, right=top)
        self.boundary_conditions = {
            p_s: {
                "left": (pybamm.Scalar(0), "Neumann"),
                "right": (pybamm.Scalar(0), "Dirichlet"),
            }
        }

    def set_initial_conditions(self, variables):
        p_s = variables["X-averaged separator pressure"]

        self.initial_conditions = {p_s: pybamm.Scalar(0)}
