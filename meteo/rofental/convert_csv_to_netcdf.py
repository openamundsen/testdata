import openamundsen as oa
import tempfile

start_date = '1900-01-01'
end_date = '2100-12-31'
out_dir = 'netcdf'

config = {
    'start_date': start_date,
    'end_date': end_date,
    'timestep': 'H',

    'input_data': {
        'meteo': {
            'dir': './csv',
            'format': 'csv',
            'crs': 'epsg:32632',
            'bounds': 'global',
        },
    },

    'domain': 'dummy',
    'resolution': 1,
    'timezone': 0,
    'crs': 'epsg:4326',
}

DUMMY_DEM = '''
ncols        1
nrows        1
xllcorner    0
yllcorner    0
cellsize    {resolution}
0
'''.strip()

with tempfile.TemporaryDirectory() as tempdir:
    config = oa.parse_config(config)
    res = config.resolution

    with open(f'{tempdir}/dem_dummy_{res}.asc', 'w') as f:
        f.write(DUMMY_DEM.format(resolution=res))

    config['input_data']['grids'] = {'dir': tempdir}
    model = oa.OpenAmundsen(config)
    model.initialize()
    meteo = model.meteo

meteo = meteo[[
    'station_name',
    'lon',
    'lat',
    'alt',
    'time',
    'temp',
    'precip',
    'rel_hum',
    'sw_in',
    'wind_speed',
]].rename_vars({
    'temp': 'tas',
    'precip': 'pr',
    'rel_hum': 'hurs',
    'sw_in': 'rsds',
    'wind_speed': 'wss',
})

meteo['pr'] /= model.timestep
meteo['pr'].attrs = {
    'standard_name': 'precipitation_flux',
    'units': 'kg m-2 s-1',
}

for station_num in range(len(meteo.station)):
    meteo_cur = meteo.isel(station=station_num).copy()

    station_id = str(meteo_cur.station.values)
    station_name = str(meteo_cur.station_name.values)
    meteo_cur.attrs = {
        'Conventions': 'CF-1.6',
        'station_name': station_name,
    }
    meteo_cur = meteo_cur.drop_vars(['station', 'station_name'])

    # Write only data from first to last non-nan timestep
    start_date, end_date = meteo_cur.dropna(dim='time').time.to_index()[[0, -1]]
    meteo_cur = meteo_cur.sel(time=slice(start_date, end_date))

    filename = f'{out_dir}/{station_id}.nc'
    print(f'Writing {filename}')
    meteo_cur.to_netcdf(filename)
