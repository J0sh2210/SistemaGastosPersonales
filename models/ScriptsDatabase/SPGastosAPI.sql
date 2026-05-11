GO
/****** Object:  StoredProcedure [dbo].[sp_ActualizarEstadoBot]    Script Date: 10/5/2026 23:55:07 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:      Josué Ramírez
-- Create Date: 30/03/2026
-- Description: SP que hara que espere el bot un monto para terminar de guardar el movimiento
-- =============================================
CREATE PROCEDURE [dbo].[sp_ActualizarEstadoBot]
(
    @IdUsuario INT,
    @NuevoEstado VARCHAR(50),
    @DatosTemporales NVARCHAR(MAX) = NULL
)
AS
BEGIN

    SET NOCOUNT ON
    BEGIN TRY
    IF NOT EXISTS (SELECT 1 FROM EstadoBotWA WHERE IdUsuario = @IdUsuario)
    BEGIN
    ;THROW 50003, 'El registro de estado para este usuario no existe',1 
    END
    SET TRANSACTION ISOLATION LEVEL READ COMMITTED
    BEGIN TRANSACTION
    UPDATE EstadoBotWA SET EstadoActual = @NuevoEstado , DatosTemporales = @DatosTemporales,
    FechaUltimaInteraccion = GETDATE()
    WHERE IdUsuario = @IdUsuario
    COMMIT TRANSACTION

    END TRY
    BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION
    DECLARE @ErrorMensaje NVARCHAR(MAX) = ERROR_MESSAGE()
    DECLARE @ErrorNumero INT = ERROR_NUMBER()
    EXEC sp_RegistrarAuditLog
    @IdUsuario = @IdUsuario,
    @Endpoint = 'sp_ActualizarEstadoBot',
    @Metodo = 'SQL',
    @MensajeError = @ErrorMensaje,
    @CodigoEstado = @ErrorNumero
    ;THROW
    END CATCH
END
GO
/****** Object:  StoredProcedure [dbo].[sp_MostrarMovimientosTotales]    Script Date: 10/5/2026 23:55:07 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:      Josué Ramírez
-- Create Date: 02/04/2026
-- Description: SP para realizar el conteo y suma de cierto tipo de movimiento ingreso o gasto
-- =============================================
CREATE PROCEDURE [dbo].[sp_MostrarMovimientosTotales]
(
    @IdUsuario INT,
    @IdTipo INT
)
AS
BEGIN

    SET NOCOUNT ON
    BEGIN TRY
    DECLARE @SaldoTotal DECIMAL(12,2)
    DECLARE @TotalMovimientos INT

    SELECT 
    @SaldoTotal = ISNULL(SUM(Monto)  , 0) FROM Movimiento
    WHERE IdUsuario = @IdUsuario AND IdTipo = @IdTipo
    SELECT
    @TotalMovimientos = ISNULL(COUNT(*), 0) FROM Movimiento
    WHERE IdUsuario = @IdUsuario AND IdTipo = @IdTipo

    SELECT 
    @SaldoTotal AS SaldoTotal,
    @TotalMovimientos AS TotalMovimientos
    END TRY
    BEGIN CATCH
    DECLARE @ErrorMensaje NVARCHAR(MAX) = ERROR_MESSAGE();
        DECLARE @ErrorNumero INT = ERROR_NUMBER();
        EXEC sp_RegistrarAuditLog
            @IdUsuario = @IdUsuario,
            @Endpoint = 'sp_MostrarMovimientosTotales', 
            @Metodo = 'SQL',
            @MensajeError = @ErrorMensaje,
            @CodigoEstado = @ErrorNumero;

        ;THROW
END CATCH
END
GO
/****** Object:  StoredProcedure [dbo].[sp_ObtenerResumenMensual]    Script Date: 10/5/2026 23:55:07 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:      Josué Ramírez
-- Create Date: 30/06/2026
-- Description: Realizar resumen de movimientos del usuario
-- =============================================
CREATE PROCEDURE [dbo].[sp_ObtenerResumenMensual]
(
    @IdUsuario INT
)
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY

        SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

        SELECT 

            ISNULL(SUM(CASE 
                WHEN IdTipo = 1 THEN Monto 
                WHEN IdTipo = 2 THEN -Monto 
                ELSE 0 END), 0) AS SaldoGlobal,
            
  
            ISNULL(SUM(CASE 
                WHEN IdTipo = 1 
                AND MONTH(FechaMovimiento) = MONTH(GETDATE()) 
                AND YEAR(FechaMovimiento) = YEAR(GETDATE()) 
                THEN Monto ELSE 0 END), 0) AS IngresosMes,
            
      
            ISNULL(SUM(CASE 
                WHEN IdTipo = 2 
                AND MONTH(FechaMovimiento) = MONTH(GETDATE()) 
                AND YEAR(FechaMovimiento) = YEAR(GETDATE()) 
                THEN Monto ELSE 0 END), 0) AS GastosMes
        FROM Movimiento
        WHERE IdUsuario = @IdUsuario;

    END TRY
    BEGIN CATCH
        DECLARE @ErrorMensaje NVARCHAR(MAX) = ERROR_MESSAGE();
        DECLARE @ErrorNumero INT = ERROR_NUMBER();

        EXEC sp_RegistrarAuditLog
            @IdUsuario = @IdUsuario,
            @Endpoint = 'sp_ObtenerResumenMensual', -- Corregido
            @Metodo = 'SQL',
            @MensajeError = @ErrorMensaje,
            @CodigoEstado = @ErrorNumero;
        
        THROW;
    END CATCH
END
GO
/****** Object:  StoredProcedure [dbo].[sp_RegistrarAuditLog]    Script Date: 10/5/2026 23:55:07 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:      Josué Ramírez
-- Create Date: 30/06/2026
-- Description: Registro errores
-- =============================================
CREATE PROCEDURE [dbo].[sp_RegistrarAuditLog]
(
    @IdUsuario INT = NULL,
    @Endpoint VARCHAR(150),
    @Metodo VARCHAR(10),
    @MensajeError NVARCHAR(MAX),
    @CodigoEstado INT
)
AS
BEGIN

    SET NOCOUNT ON
IF @IdUsuario IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Usuario WHERE IdUsuario = @IdUsuario)
    BEGIN
        SET @IdUsuario = NULL
    END

    INSERT INTO AuditLog (
        IdUsuario, 
        Endpoint, 
        Metodo, 
        MensajeError, 
        CodigoEstado, 
        FechaRegistro
    )
    VALUES (
        @IdUsuario, 
        @Endpoint, 
        @Metodo, 
        @MensajeError, 
        @CodigoEstado, 
        GETDATE()
    )
END
GO
/****** Object:  StoredProcedure [dbo].[sp_RegistrarMovimiento]    Script Date: 10/5/2026 23:55:07 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:      Josué Ramírez
-- Create Date: 30/03/2026
-- Description: Registro de movimiento del usuario
-- =============================================
CREATE PROCEDURE [dbo].[sp_RegistrarMovimiento]
(
    @IdUsuario INT,
    @Monto DECIMAL (12,2),
    @Concepto VARCHAR(150) NULL,
    @Tipo INT,
    @CategoriaTag VARCHAR(30) = 'General',
    @FuenteRegistro VARCHAR(60)

)

AS
BEGIN

    SET NOCOUNT ON
    DECLARE @IdTipo INT
    BEGIN TRY
    
    IF NOT EXISTS(SELECT 1 FROM Usuario WHERE IdUsuario = @IdUsuario)
    BEGIN
        ;THROW 50001,'Usuario no existente', 1
    END
    IF @Monto <= 0 
    BEGIN
        ;THROW 50003, 'El monto debe ser mayor a 0', 1
    END
    SET TRANSACTION ISOLATION LEVEL READ COMMITTED
    BEGIN TRANSACTION 


    INSERT INTO Movimiento (IdUsuario, Monto, Concepto, IdTipo, CategoriaTag, FuenteRegistro, FechaMovimiento ) 
    VALUES (@IdUsuario, @Monto, @Concepto, @Tipo, @CategoriaTag, @FuenteRegistro, GETDATE())

    UPDATE EstadoBotWA SET EstadoActual = 'IDLE', DatosTemporales = NULL 
    WHERE IdUsuario = @IdUsuario

    COMMIT TRANSACTION
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION
        DECLARE @ErrorMensaje NVARCHAR(MAX) = ERROR_MESSAGE()
        DECLARE @ErrorNumero INT = ERROR_NUMBER()
        EXEC sp_RegistrarAuditLog
        @IdUsuario = @IdUsuario,
        @Endpoint = 'sp_ActualizarEstadoBot',
        @Metodo = 'SQL',
        @MensajeError = @ErrorMensaje,
        @CodigoEstado = @ErrorNumero
        ;THROW
    END CATCH
END
GO
/****** Object:  StoredProcedure [dbo].[sp_RegistrarUsuarioCompleto]    Script Date: 10/5/2026 23:55:07 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:      Josué Ramírez
-- Create Date: 30/03/2026
-- Description: El siguiente sp maneja el registro de usuario de ambos tipos,
-- el registro por gmail y registro manual
-- =============================================

CREATE PROCEDURE [dbo].[sp_RegistrarUsuarioCompleto]
(
@PrimerNombre VARCHAR(30),
@SegundoNombre VARCHAR(30) = NULL,
@PrimerApellido VARCHAR(30),
@SegundoApellido VARCHAR(30) = NULL,
@Correo VARCHAR(30),
@TelefonoWA VARCHAR(15),


@ProviderUserId VARCHAR(MAX),
@Contrasena VARCHAR(MAX) NULL,
@IdProvider INT
)
AS
BEGIN

    SET NOCOUNT ON
    BEGIN TRY
    DECLARE @IdRol INT
    SELECT @IdRol = IdRol FROM Rol WHERE NombreRol = 'Usuario'
    IF @IdRol IS NULL
    BEGIN
        ;THROW 50001, 'El rol no existe',1 
    END
    IF EXISTS (SELECT 1 FROM Usuario WHERE Correo = @Correo)
    BEGIN
        ;THROW 50002, 'El correo ya existe',1
    END
    IF EXISTS (SELECT 1 FROM Usuario WHERE TelefonoWA = @TelefonoWA)
    BEGIN
        ;THROW 50003, 'El Telefono ya existe',1
    END

    SET TRANSACTION ISOLATION LEVEL READ COMMITTED
    BEGIN TRANSACTION
    DECLARE @IdUsuario INT
    INSERT INTO Usuario (PrimerNombre, SegundoNombre, PrimerApellido, SegundoApellido,
    Correo, TelefonoWA, IdRol
    ) VALUES (@PrimerNombre, @SegundoNombre, @PrimerApellido, @SegundoApellido, @Correo,
    @TelefonoWA, @IdRol)

     SET @IdUsuario = SCOPE_IDENTITY()

     INSERT INTO Credencial (ProviderUserId, Contrasena, IdUsuario, IdProvider) VALUES
     (@ProviderUserId, @Contrasena, @IdUsuario, @IdProvider)

     INSERT INTO EstadoBotWA (IdUsuario, EstadoActual) VALUES (@IdUsuario, 'IDLE')
     COMMIT TRANSACTION
    SELECT @IdUsuario AS IdUsuarioNuevo
    END TRY
    BEGIN CATCH

    IF @@TRANCOUNT > 0
    ROLLBACK TRANSACTION
    DECLARE @ErrorMensaje NVARCHAR(MAX) = ERROR_MESSAGE()
    DECLARE @ErrorNumero INT = ERROR_NUMBER()
    EXEC sp_RegistrarAuditLog
    @IdUsuario = @IdUsuario,
    @Endpoint = 'sp_ActualizarEstadoBot',
    @Metodo = 'SQL',
    @MensajeError = @ErrorMensaje,
    @CodigoEstado = @ErrorNumero
    ;THROW

    END CATCH

END
GO
/****** Object:  StoredProcedure [dbo].[sp_ValidarAccesoWhatsapp]    Script Date: 10/5/2026 23:55:07 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:      Josué Ramírez
-- Create Date: 30/06/2026
-- Description: SP que utilzará el bot de Whatsapp para validar existencia de usuario,
-- y su estado este activo
-- =============================================
CREATE PROCEDURE [dbo].[sp_ValidarAccesoWhatsapp]
(
    @TelefonoRecibido VARCHAR(20)
)

AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @IdUsuario INT;
    DECLARE @Nombre VARCHAR(30);
    DECLARE @EstadoActualUsuario CHAR(1);
    DECLARE @EstadoBot VARCHAR(50);
    DECLARE @DatosTemporales NVARCHAR(MAX)

    BEGIN TRY
       
        SELECT 
            @IdUsuario = u.IdUsuario,
            @Nombre = u.PrimerNombre,
            @EstadoActualUsuario = u.Estado,
            @EstadoBot = eb.EstadoActual,
            @DatosTemporales = eb.DatosTemporales

        FROM Usuario u (HOLDLOCK)
        INNER JOIN EstadoBotWA eb ON u.IdUsuario = eb.IdUsuario
        WHERE u.TelefonoWA = @TelefonoRecibido;

      
        IF @IdUsuario IS NULL
        BEGIN
            ;THROW 50001, 'Usuario no registrado', 1
        END
        IF @EstadoActualUsuario <> 'A'
        BEGIN
            ;THROW 50002, 'Usuario Inactivo', 1
        END
        SELECT 
            @IdUsuario AS IdUsuario, 
            @Nombre AS PrimerNombre, 
            ISNULL(@EstadoBot, 'IDLE') AS EstadoActual,
            @DatosTemporales AS DatosTemporales

    END TRY
    BEGIN CATCH
        DECLARE @ErrorMensaje NVARCHAR(MAX) = ERROR_MESSAGE()
        DECLARE @ErrorNumero INT = ERROR_NUMBER()
        EXEC sp_RegistrarAuditLog
        @IdUsuario = @IdUsuario,
        @Endpoint = 'sp_ActualizarEstadoBot',
        @Metodo = 'SQL',
        @MensajeError = @ErrorMensaje,
        @CodigoEstado = @ErrorNumero
        ;THROW
    END CATCH
END
GO