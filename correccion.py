import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

################################# Cargar datos #################################################  
df1 = pd.read_json("productos.json")
print(df1)
df2 = pd.read_xml("productos.xml")
print(df2)
df3 = pd.read_csv("productos.txt")
print(df3) #300 - 399

conn = sqlite3.connect("productos.db")
df4 = pd.read_sql_query("SELECT * FROM productos", conn)
conn.close()
print(df4) 
#1 - 100 

#100 - 199
#300 - 399
#400 - 499
############################### Consolidar ####################################################
df=pd.concat([df1,df2,df3,df4],ignore_index=True)
#df.set_index("id", inplace=True)
print("\n############ Revisar las primeras filas y los tipos de datos de cada columna ###########")
print(df.head(10))  
print(df.info())


print("\n############ Identificar valores nulos, vacíos o incorrectos. ###########")
print(df.isnull().sum())




print("\n###### Convertir columnas numéricas (id, precio_compra, stock, precio_venta_publico) al tipo correcto ###########")
df["id"] = pd.to_numeric(df["id"], errors="coerce")
df["precio_compra"] = pd.to_numeric(df["precio_compra"], errors="coerce")
df["stock"] = pd.to_numeric(df["stock"], errors="coerce")
df["precio_venta_publico"] = pd.to_numeric(df["precio_venta_publico"], errors="coerce")
df.info()
print(df.isnull().sum())       #totalNulosPrecio/len(df[precio])  10/100 = 10% de la data es sucia

print("\n############ Calcular el porcentaje de datos sucios en cada columna ###########")
total = len(df)
nulos = df.isnull().sum()
porcentaje = (nulos / total) * 100
print(porcentaje.round(2).astype(str) + " %")

#[ print(x) for x in df["nombre"]]

print("\n############ IMPUTAR VALORES FALTANTES  ###########")
print("\n############ Usar la mediana para precio_compra  ###########")
mediana_precio = df["precio_compra"].median()
df["precio_compra"].fillna(mediana_precio, inplace=True)

print("\n############ Calcular precio_venta_publico faltante como precio_compra × margen fijo  ###########")
margen = 0.095
df["precio_venta_publico"] = df["precio_venta_publico"].fillna(df["precio_compra"] * margen)

print("\n############ Completar categorías y proveedores con etiquetas genéricas  ###########")
df["categoria"].fillna("Sin categoría", inplace=True)
df.loc[df['categoria'] == 'error', 'categoria'] = 'Sin categoría'

df["proveedor"].fillna("Proveedor desconocido", inplace=True)
df["stock"].fillna(0, inplace=True) # Se reemplaza con cero porque se desconoce cuantas unidades reales hay
df["nombre"].fillna("Producto sin nombre", inplace=True) #Productos sin nombre valido o reconocido

print("COMPROBANDO:\n")
print(df.isnull().sum())


print("\nStock negativo")
print(df[df['stock'] < 0])

print("\nPrecio de venta menor al precio de compra")
#print(df[df['precio_venta_publico'] < df['precio_compra']])
print(len(df)) # loguitud de todo el df =399

df = df[df['precio_venta_publico'] >= df['precio_compra']]
print("\n")
print(len(df)) #Quitando  valores incorrectos = 306 DATOS OPTIMOS


print("\nEliminar Duplicados por id")
df = df.drop_duplicates(subset=['id'], keep='first')
print("Duplicados: ",df[df['id'].duplicated(keep=False)])


################################### PROCESAMIENTO ######################################
print("\nCalcular mínimo, máximo, media, mediana y desviación estándar de precio_compra, precio_venta_publico y stock. ")
for col in ['precio_compra', 'precio_venta_publico', 'stock']:
    print(f"\nEstadísticas para {col}:")
    print("Mínimo:", df[col].min())
    print("Máximo:", df[col].max())
    print("Media:", df[col].mean())
    print("Mediana:", df[col].median())
    print("Desviación estándar:", df[col].std())


print("\nComparar si los precios de venta tienen una distribución más dispersa que los de compra.")
print("Dispersión de precio_compra")
print("Rango:", df['precio_compra'].max() - df['precio_compra'].min())
print("Desviación estándar:", df['precio_compra'].std())

print("\nDispersión de precio_venta_publico")
print("Rango:", df['precio_venta_publico'].max() - df['precio_venta_publico'].min())
print("Desviación estándar:", df['precio_venta_publico'].std())

#Si la desviación estándar y el rango de precio_venta_publico son mayores que los de precio_compra, entonces los precios de venta están más dispersos.

#Si son menores, significa que los precios de compra tienen más variabilidad.

print("\nIdentificar outliers (valores extremos) en precios y stock")

for col in ['precio_compra', 'precio_venta_publico', 'stock']:
    Q1 = df[col].quantile(0.25) #"<Q1" 
    print("Q1: ",Q1) 
    #2.91
   
    Q3 = df[col].quantile(0.75)  #print(Q3)  ">Q3"
    print("Q3: ", Q3)
    #7.06
    IQR = Q3 - Q1   #Rango Intercuartílico # Datos agrupados
    outliers = df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)] # Extremos
    print(f"\nOutliers en {col}:")
    print(outliers[[col]])

#Si el bloque imprime filas, esos son tus outliers.

#Si no imprime nada, no hay valores extremos según la regla IQR.

print("\nContar el número de productos únicos en cada categoría.")
# Contar productos únicos por categoría usando 'id'
productos_por_categoria = df.groupby('categoria')['id'].nunique()

print("\nNúmero de productos únicos en cada categoría:")
print(productos_por_categoria)

print("\nCalcular el stock total por categoría y el stock promedio por producto.")
stock_total_categoria = df.groupby('categoria')['stock'].sum()

print("\nStock total por categoría:")
print(stock_total_categoria)

print("\nCalcular el precio promedio de compra y de venta por categoría.")
precios_promedio_categoria = df.groupby('categoria')[['precio_compra', 'precio_venta_publico']].mean()

print("\nPrecio promedio de compra y venta por categoría:")
print(precios_promedio_categoria)

print("\nComparar categorías para ver cuál tiene la mayor diferencia entre precio de compra y venta.")
# Calcular promedios de compra y venta por categoría
precios_promedio = df.groupby('categoria')[['precio_compra', 'precio_venta_publico']].mean()

# Agregar columna con la diferencia (No hay negativos) ¡que categoria nos da mayor margen de ganancia
precios_promedio['diferencia'] = precios_promedio['precio_venta_publico'] - precios_promedio['precio_compra']

print("\nDiferencia promedio entre precio de venta y compra por categoría:")
print(precios_promedio) #Analizar las diferencias y concluir


# Identificar la categoría con mayor diferencia
categoria_max = precios_promedio['diferencia'].idxmax()
valor_max = precios_promedio['diferencia'].max()

print(f"\nLa categoría con mayor diferencia es: {categoria_max} ({valor_max:.2f})")

print("\n#########Ordenar las categorías de mayor a menor stock y discutir si coincide con las categorías más rentables.")
stock_por_categoria = df.groupby('categoria')['stock'].sum().sort_values(ascending=True)

print("\nStock total por categoría (ordenado de mayor a menor):")
print(stock_por_categoria)


print("\n#################Calcular el margen absoluto (precio_venta_publico - precio_compra) para cada producto.")
df['margen_absoluto'] = df['precio_venta_publico'] - df['precio_compra']

print("\nPrimeros registros con margen absoluto:")
print(df[['id', 'nombre', 'precio_compra', 'precio_venta_publico', 'margen_absoluto']].head(10))

print("\n################Calcular el margen porcentual (margen_abs / precio_compra)")
df['margen_porcentual'] = df['margen_absoluto'] / df['precio_compra']

print("\nPrimeros registros con margen porcentual:")
print(df[['id', 'nombre', 'precio_compra', 'precio_venta_publico', 'margen_absoluto', 'margen_porcentual']].head())

print("\n###############Analizar la distribución de márgenes por categoría")
# Resumen de márgenes por categoría
margen_stats = df.groupby('categoria')[['margen_absoluto', 'margen_porcentual']].describe()

print("\nDistribución de márgenes por categoría:")
print(margen_stats)

print("\n¿Qué categorías tienen márgenes más altos en promedio?")
# Promedio de márgenes por categoría
margen_promedio = df.groupby('categoria')[['margen_absoluto','margen_porcentual']].mean()

print("\nPromedio de márgenes por categoría:")
print(margen_promedio.sort_values('margen_absoluto', ascending=False))
####################################################################################

print("\n¿Qué categorías tienen mayor variabilidad en márgenes?")
variabilidad_margenes = df.groupby('categoria')[['margen_absoluto','margen_porcentual']].std()

print("\nVariabilidad (desviación estándar) de márgenes por categoría:")
print(variabilidad_margenes.sort_values('margen_absoluto', ascending=False))

print("\nListar los 10 productos con mayor stock y analizar si pertenecen a las mismas categorías o proveedores.")
top10_stock = df.sort_values('stock', ascending=False).head(10)

print("\nTop 10 productos con mayor stock:")
print(top10_stock[['id','nombre','categoria','proveedor','stock']])

print("\nAnalizar si pertenecen a las mismas categorias o a los mis mos proveedores")
print("\nDistribución de categorías en el Top 10:")
print(top10_stock['categoria'].value_counts())
print("\nDistribución de proveedores en el Top 10:")
print(top10_stock['proveedor'].value_counts())

print("\nComparar si los productos más rentables también son los más vendidos (stock alto).")
# Top 10 productos más rentables por margen absoluto
top10_rentables = df.sort_values('margen_absoluto', ascending=False).head(10)

print("\nTop 10 productos más rentables:")
print(top10_rentables[['id','nombre','categoria','proveedor','margen_absoluto','stock']])


print("\nIdentificar los productos con mayor stock")
top10_stock = df.sort_values('stock', ascending=False).head(10)

print("\nTop 10 productos con mayor stock:")
print(top10_stock[['id','nombre','categoria','proveedor','stock','margen_absoluto']])

print("\nComparativa")
# Comparar si hay productos en común
productos_comunes = set(top10_rentables['id']).intersection(set(top10_stock['id']))

print("\nProductos que son a la vez de mayor stock y más rentables:")
print(df[df['id'].isin(productos_comunes)][['id','nombre','categoria','proveedor','stock','margen_absoluto']])

print("\nDetectar si hay productos con alto stock pero baja rentabilidad (riesgo de pérdida).")
# Calcular umbrales
umbral_stock = df['stock'].quantile(0.75)   # percentil 75 de stock
umbral_margen = df['margen_absoluto'].mean()  # promedio de margen absoluto

# Filtrar productos con alto stock pero baja rentabilidad
riesgo_perdida = df[(df['stock'] >= umbral_stock) & (df['margen_absoluto'] < umbral_margen)]

print("\nProductos con alto stock pero baja rentabilidad (riesgo de pérdida):")
print(riesgo_perdida[['id','nombre','categoria','proveedor','stock','margen_absoluto','margen_porcentual']])

#Si aparecen productos en esta lista, significa que tienes mucho inventario acumulado en artículos poco rentables.

##################################################################################################################
########################################### VISUALIZACION ########################################################
##################################################################################################################
##########Usar Matplotlib y Seaborn para graficar:
#	Histograma de precios de compra.
plt.figure(figsize=(8,6))
sns.histplot(df['precio_compra'], bins=20, kde=True)
plt.title('Histograma de precios de compra')
plt.xlabel('Precio de compra')
plt.ylabel('Frecuencia')
plt.show()

#	Gráfico de dispersión: precio de compra vs precio de venta.
plt.figure(figsize=(8,6))
sns.scatterplot(x='precio_compra', y='precio_venta_publico', data=df)
plt.title('Precio de compra vs Precio de venta')
plt.xlabel('Precio de compra')
plt.ylabel('Precio de venta público')
plt.show()

#	Barras: stock total por categoría.
plt.figure(figsize=(10,6))
stock_categoria = df.groupby('categoria')['stock'].sum().reset_index()
sns.barplot(x='categoria', y='stock', data=stock_categoria)
plt.xticks(rotation=45)
plt.title('Stock total por categoría')
plt.xlabel('Categoría')
plt.ylabel('Stock total')
plt.show()

#	Caja (boxplot): distribución del margen porcentual por categoría.
plt.figure(figsize=(10,6))
sns.boxplot(x='categoria', y='margen_porcentual', data=df)
plt.xticks(rotation=45)
plt.title('Distribución del margen porcentual por categoría')
plt.xlabel('Categoría')
plt.ylabel('Margen porcentual')
plt.show()










