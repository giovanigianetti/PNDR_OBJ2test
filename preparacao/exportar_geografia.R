suppressPackageStartupMessages({library(sf);library(jsonlite)})
p <- 'C:/Users/Giovani/Documents/Codex/2026-11-18/t'
m <- readRDS(file.path(p,'outputs/final_pndr/insumos/municipios2022_simplificados.rds'))
v <- read.csv(file.path(p,'outputs/final_pndr/tabelas/indicadores_municipais.csv'))
m <- m[as.numeric(m$CD_MUN) %in% v$codmun,]
stopifnot(nrow(m)==5570)
m <- st_transform(m,4326)
sf_use_s2(FALSE)
m <- m[,c('CD_MUN')]
names(m)[1] <- 'codmun'
m <- st_simplify(m,dTolerance=0.008,preserveTopology=TRUE)
st_write(m,file.path(p,'work/paineis_pndr/municipios2022.geojson'),delete_dsn=TRUE,quiet=TRUE,layer_options='COORDINATE_PRECISION=4')
pts <- suppressWarnings(st_point_on_surface(m)); coords <- st_coordinates(pts)
write_json(data.frame(codmun=m$codmun,lon=coords[,1],lat=coords[,2]),file.path(p,'work/paineis_pndr/centroides.json'),auto_unbox=TRUE,digits=6)
cat(nrow(m),'municipios exportados\n')
