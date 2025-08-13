CREATE PROCEDURE usp_ActualizarStockPorVenta
    -- Par�metros que recibe el procedimiento desde tu aplicaci�n Python
    @NombreProducto NVARCHAR(255),
    @CantidadVendida INT
AS
BEGIN
    -- Esta instrucci�n evita que se env�en mensajes de "filas afectadas" a la aplicaci�n
    SET NOCOUNT ON;

    -- Se actualiza el stock del producto correspondiente
    UPDATE Productos
    SET
        Stock = Stock - @CantidadVendida -- Resta la cantidad vendida al stock actual
    WHERE
        Nombre = @NombreProducto          -- Busca el producto por su nombre
        AND Stock >= @CantidadVendida;    -- �Importante! Solo realiza la resta si hay stock suficiente
END
GO