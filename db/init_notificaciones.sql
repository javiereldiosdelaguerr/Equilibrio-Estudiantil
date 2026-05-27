CREATE DATABASE IF NOT EXISTS db_notificaciones;
USE db_notificaciones;
CREATE TABLE IF NOT EXISTS notificaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    mensaje TEXT NOT NULL,
    leida BOOLEAN DEFAULT FALSE,
    creada_en DATETIME DEFAULT CURRENT_TIMESTAMP
);
