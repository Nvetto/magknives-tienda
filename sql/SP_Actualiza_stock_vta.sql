CREATE PROCEDURE usp_ActualizarStockPorVenta
    -- Parámetros que recibe el procedimiento desde tu aplicación Python
    @NombreProducto NVARCHAR(255),
    @CantidadVendida INT
AS
BEGIN
    -- Esta instrucción evita que se envíen mensajes de "filas afectadas" a la aplicación
    SET NOCOUNT ON;

    -- Se actualiza el stock del producto correspondiente
    UPDATE Productos
    SET
        Stock = Stock - @CantidadVendida -- Resta la cantidad vendida al stock actual
    WHERE
        Nombre = @NombreProducto          -- Busca el producto por su nombre
        AND Stock >= @CantidadVendida;    -- ¡Importante! Solo realiza la resta si hay stock suficiente
END
GO