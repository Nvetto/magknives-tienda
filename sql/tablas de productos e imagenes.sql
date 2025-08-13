-- =================================================================
-- PASO 1: CREACIÓN DE LAS TABLAS
-- =================================================================
-- Primero, creamos la tabla principal de Productos.
-- IDENTITY(1,1) hace que el ProductoID se autoincremente (1, 2, 3...)
CREATE TABLE Productos (
    ProductoID INT PRIMARY KEY IDENTITY(1,1),
    Nombre NVARCHAR(255) NOT NULL,
    Descripcion NVARCHAR(MAX),
    Precio DECIMAL(10, 2) NOT NULL,
    Stock INT NOT NULL,
    Categoria NVARCHAR(100)
);
GO

-- Segundo, creamos la tabla para las imágenes.
-- El ProductoID aquí es una 'Clave Foránea' que se conecta con la tabla Productos.
CREATE TABLE ImagenesProducto (
    ImagenID INT PRIMARY KEY IDENTITY(1,1),
    ProductoID INT FOREIGN KEY REFERENCES Productos(ProductoID),
    URL NVARCHAR(500) NOT NULL
);
GO

-- =================================================================
-- PASO 2: INSERCIÓN DE DATOS DESDE STOCK.JSON
-- =================================================================
-- Ahora, vaciamos los datos de tus productos en las tablas que creamos.

-- Producto 1: Cazador Coral
INSERT INTO Productos (Nombre, Descripcion, Precio, Stock, Categoria)
VALUES ('Cazador Coral', 'Cuchillo Cazador con mango de coral marino en resina y hoja de acero templado.', 15000, 1, 'personalizados');
-- Insertamos sus imágenes, usando el ID 1 que se acaba de generar
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (1, 'Imagenes/Cazador Coral marino/1.jpg');
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (1, 'Imagenes/Cazador Coral marino/2.jpg');
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (1, 'Imagenes/Cazador Coral marino/4.jpg');
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (1, 'Imagenes/Cazador Coral marino/5.jpg');
GO

-- Producto 2: Cazador en acero Damasco
INSERT INTO Productos (Nombre, Descripcion, Precio, Stock, Categoria)
VALUES ('Cazador en acero Damasco', 'Un cazador estilo nessmuk hecho en San-mai damasco con cachas de burl de imbuia.', 15000, 4, 'personalizados');
-- Insertamos sus imágenes con el ID 2
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (2, 'Imagenes/Cazador Damasco/1.jpg');
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (2, 'Imagenes/Cazador Damasco/2.jpg');
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (2, 'Imagenes/Cazador Damasco/3.jpg');
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (2, 'Imagenes/Cazador Damasco/1.jpg');
GO

-- Producto 3: Verijero criollo
INSERT INTO Productos (Nombre, Descripcion, Precio, Stock, Categoria)
VALUES ('Verijero criollo', 'Construido en 5160 de 4mm con vaciado cóncavo, guarda y separador de inoxidable, virola de alpaca y cabo de Dalbergia Nigra.', 15000, 5, 'personalizados');
-- Insertamos sus imágenes con el ID 3
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (3, 'Imagenes/Verijero/1.jpg');
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (3, 'Imagenes/Verijero/2.jpg');
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (3, 'Imagenes/Verijero/3.jpg');
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (3, 'Imagenes/Verijero/4.jpg');
GO

-- Producto 4: Facón de lima Nicholson antigua
INSERT INTO Productos (Nombre, Descripcion, Precio, Stock, Categoria)
VALUES ('Facón de lima Nicholson antigua', 'Hoja de acero W1 de una lima Nicholson americana antigua, 6mm de espesor, bisel plano con terminación satinada, encabado en burl de lenga.', 15000, 5, 'personalizados');
-- Insertamos sus imágenes con el ID 4
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (4, 'Imagenes/Lima Nicholson/1.jpg');
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (4, 'Imagenes/Lima Nicholson/3.jpg');
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (4, 'Imagenes/Lima Nicholson/2.jpg');
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (4, 'Imagenes/Lima Nicholson/4.jpg');
GO

-- Producto 5: Cazador
INSERT INTO Productos (Nombre, Descripcion, Precio, Stock, Categoria)
VALUES ('Cazador', 'Fabricado en acero 5160 de 4mm pasivado con stonewash, espiga distal, separadores de bronce, pin mosaico y cachas de wengue añejado.', 15000, 5, 'cazadores');
-- Insertamos sus imágenes con el ID 5
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (5, 'Imagenes/Cazador/1.jpg');
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (5, 'Imagenes/Cazador/2.jpg');
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (5, 'Imagenes/Cazador/3.jpg');
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (5, 'Imagenes/Cazador/4.jpg');
GO

-- Producto 6: Cazador itin
INSERT INTO Productos (Nombre, Descripcion, Precio, Stock, Categoria)
VALUES ('Cazador itin', 'Cazador/cuereador integral. Hoja de 1095, aprox 2mm de espesor con terminación stonewash y cabo de Itin.', 15000, 0, 'cazadores');
-- Insertamos sus imágenes con el ID 6
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (6, 'Imagenes/Cazador itin/1.jpg');
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (6, 'Imagenes/Cazador itin/2.jpg');
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (6, 'Imagenes/Cazador itin/1.jpg');
INSERT INTO ImagenesProducto (ProductoID, URL) VALUES (6, 'Imagenes/Cazador itin/2.jpg');
GO


-- Para ver todos tus productos
SELECT * FROM Productos;

-- Para ver todas las imágenes y a qué producto pertenecen
SELECT * FROM ImagenesProducto;