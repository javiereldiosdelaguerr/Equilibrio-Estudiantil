CREATE DATABASE IF NOT EXISTS db_recomendaciones;
USE db_recomendaciones;
CREATE TABLE IF NOT EXISTS recomendaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    estado_mood VARCHAR(50),
    total_sesiones INT DEFAULT 0,
    recomendacion TEXT NOT NULL,
    generada_en DATETIME DEFAULT CURRENT_TIMESTAMP
);
