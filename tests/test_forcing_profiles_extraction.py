from pathlib import Path
import dateutil.parser
import datetime

import xarray as xr
import numpy as np
import pytest

import pytraj.produce.lagrangian_trajectory
from pytraj.produce import forcing_profiles


def test_create_dummy_forcing_from_stationary_trajectory():
    ds_traj = pytraj.produce.lagrangian_trajectory.stationary.extract_trajectory(
        lat0=-10, lon0=40,
        t0=dateutil.parser.parse("2020-01-22T12:00"),
        t_max=dateutil.parser.parse("2020-01-24T12:00"),
        dt=datetime.timedelta(hours=4),
    )

    da_levels = xr.DataArray(
        np.array([100e3, 90e3, 80e3, 70e3]),
        attrs=dict(long_name='pressure levels', units='Pa')
    )

    ds_forcing_profiles = forcing_profiles.dummy.extract_forcing_profiles(
        ds_traj=ds_traj,
        required_variables=["ddt__qv",],
        da_levels=da_levels
    )

def test_create_era5_forcing_from_stationary_trajectory():
    ds_traj = pytraj.produce.lagrangian_trajectory.stationary.extract_trajectory(
        lat0=-10, lon0=40,
        t0=dateutil.parser.parse("2020-01-22T12:00"),
        t_max=dateutil.parser.parse("2020-01-24T12:00"),
        dt=datetime.timedelta(hours=4),
    )

    with pytest.raises(NotImplementedError):
        dx = 25
        da_levels = xr.DataArray(
            0.5*dx + np.arange(0, 5e3, dx),
            attrs=dict(long_name='height levels', units='m')
        )

        ds_forcing_profiles = forcing_profiles.era5_extract_forcing_profiles(
            ds_traj=ds_traj,
            required_variables=["ddt__qv",],
            da_levels=da_levels
        )

    with pytest.raises(forcing_profiles.era5.InvalidLevelsDefinition):
        da_levels = xr.DataArray(
            np.array([100e3, 90e3, 80e3, 70e3]),
            attrs=dict(long_name='pressure levels', units='Pa')
        )

        ds_forcing_profiles = forcing_profiles.era5_extract_forcing_profiles(
            ds_traj=ds_traj,
            required_variables=["ddt__qv",],
            da_levels=da_levels
        )

# testing command line interface
def test_main():
    fn_trajectory = "trajectory_test.nc"
    pytraj.produce.lagrangian_trajectory.main(
        lat0=-10, lon0=40,
        t0=dateutil.parser.parse("2020-01-22T12:00"),
        t_max=dateutil.parser.parse("2020-01-24T12:00"),
        dt=datetime.timedelta(hours=4),
        trajectory_type='stationary',
        out_filename=fn_trajectory,
    )

    fn_forcing_profiles = "forcing_profiles.nc"
    forcing_profiles.main(
        fn_trajectory=fn_trajectory,
        source_data="dummy",
        out_filename=fn_forcing_profiles,
    )

    p_traj = Path(fn_trajectory)
    p_forcing = Path(fn_forcing_profiles)

    assert p_forcing.exists()
    p_traj.unlink()
    p_forcing.unlink()
