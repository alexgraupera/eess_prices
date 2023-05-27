"""Constant values for ees_prices."""

DOMAIN = "eess_prices"

CONF_MUNICIPIO = "municipio"
CONF_MUNICIPIO_ID = "municipio_id"
CONF_MUNICIPIO_FUEL_TYPE = "municipio_fuel_type"
CONF_MUNICIPIO_FUEL_TYPE_DESCRIPTION = "municipio_fuel_type_description"
CONF_MUNICIPIOS_URL_LIST = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/Listados/Municipios/"
CONF_MUNICIPIO_FILTER_URL = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/FiltroMunicipio/"
CONF_GAS_95_ES = "GAS_95_ES"
CONF_GAS_98_ES = "GAS_98_ES"
CONF_GAS_DIESEL_A = "GAS_DIESEL_A"
CONF_FUEL_TYPE = {
    CONF_GAS_95_ES: "Gasolina 95 ES",
    CONF_GAS_98_ES: "Gasolina 98 ES",
    CONF_GAS_DIESEL_A: "Gasoleo A"
}

KEY_LISTA_EESS_PRECIO = "ListaEESSPrecio"
KEY_GAS_95_ES = "Precio Gasolina 95 E5"
KEY_GAS_98_ES = "Precio Gasolina 98 E5"
KEY_GAS_DIESEL_A = "Precio Gasoleo A"
KEY_FUEL_TYPE = {
    CONF_GAS_95_ES: KEY_GAS_95_ES,
    CONF_GAS_98_ES: KEY_GAS_98_ES,
    CONF_GAS_DIESEL_A: KEY_GAS_DIESEL_A    
}
KEY_STATION_NAME = "Rótulo"
KEY_STATION_LATITUDE = "Latitud"
KEY_STATION_LONGITUDE = "Longitud (WGS84)"
KEY_STATION_OPENING_HOURS = "Horario"
KEY_STATION_ADDRESS = "Dirección"