-- =================================================================
-- PASO 1: CREACIÓN DE LA TABLA DE ROLES
-- Esta tabla es un catálogo de los tipos de usuarios que tendremos.
-- =================================================================
CREATE TABLE Roles (
    RolID INT PRIMARY KEY,
    NombreRol NVARCHAR(50) NOT NULL UNIQUE
);
GO

-- Insertamos los roles iniciales que necesitará el sistema.
INSERT INTO Roles (RolID, NombreRol) VALUES (1, 'admin');
INSERT INTO Roles (RolID, NombreRol) VALUES (2, 'cliente');
GO


-- =================================================================
-- PASO 2: CREACIÓN DE LA TABLA DE USUARIOS
-- Aquí se guardará la información de cada persona registrada.
-- =================================================================
CREATE TABLE Usuarios (
    UsuarioID INT PRIMARY KEY IDENTITY(1,1),
    Nombre NVARCHAR(100),
    Apellido NVARCHAR(100),
    Email NVARCHAR(255) NOT NULL UNIQUE,
    -- Columna CRÍTICA: Nunca guardaremos la contraseña, solo su versión encriptada (hash).
    HashContrasena NVARCHAR(255) NOT NULL,
    FechaRegistro DATETIME2 DEFAULT GETDATE()
);
GO


-- =================================================================
-- PASO 3: CREACIÓN DE LA TABLA PUENTE (USUARIO-ROLES)
-- Esta tabla nos permite asignar uno o más roles a cada usuario.
-- =================================================================
CREATE TABLE UsuarioRoles (
    UsuarioID INT FOREIGN KEY REFERENCES Usuarios(UsuarioID),
    RolID INT FOREIGN KEY REFERENCES Roles(RolID),
    -- Definimos una clave primaria compuesta para evitar asignar el mismo rol dos veces al mismo usuario.
    PRIMARY KEY (UsuarioID, RolID)
);
GO

select * from Roles;

select * from Usuarios;

Select * from UsuarioRoles;

-- =========== SCRIPT PARA CREAR USUARIO ADMINISTRADOR ===========
DECLARE @Nombre NVARCHAR(100) = 'Nicolas';
DECLARE @Apellido NVARCHAR(100) = 'Vettovalli';
DECLARE @Email NVARCHAR(255) = 'nicovettovalli@hotmail.com';
DECLARE @HashDeContrasena NVARCHAR(255) = 'scrypt:32768:8:1$PJjrTrPqYZkccoyW$310f750c32751cfebdb2f271246fe6055583d27b1d1e6123a8bcae4e90206bd4f12b09da068f994d62b550c4b2617eaf2b28258c90b1b2fec88a8a265643d9f6';

-- -------------------------------------------------------------------

-- 3. Insertamos el nuevo usuario en la tabla Usuarios
INSERT INTO Usuarios (Nombre, Apellido, Email, HashContrasena)
VALUES (@Nombre, @Apellido, @Email, @HashDeContrasena);

-- 4. Obtenemos el ID del usuario que acabamos de crear
DECLARE @NuevoUsuarioID INT = SCOPE_IDENTITY();

-- 5. Asignamos el rol de 'admin' (que tiene RolID = 1) a este nuevo usuario
INSERT INTO UsuarioRoles (UsuarioID, RolID)
VALUES (@NuevoUsuarioID, 1);

PRINT '¡Usuario administrador creado exitosamente!';
GO