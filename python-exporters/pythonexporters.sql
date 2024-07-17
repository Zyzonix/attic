-- phpMyAdmin SQL Dump
-- version 5.2.1deb1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Apr 26, 2024 at 07:53 PM
-- Server version: 10.11.6-MariaDB-0+deb12u1-log
-- PHP Version: 8.2.18

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `pythonexporters`
--

-- --------------------------------------------------------

--
-- Table structure for table `shellydata`
--

CREATE TABLE `shellydata` (
  `time_utc` datetime NOT NULL,
  `time_local` datetime NOT NULL,
  `shelly_current_power` float NOT NULL,
  `shelly_cpu_temp` float NOT NULL,
  `shelly_ram_total` float NOT NULL,
  `shelly_ram_free` float NOT NULL,
  `shelly_fs_total` float NOT NULL,
  `shelly_fs_free` float NOT NULL,
  `shelly_total_power` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `watchdogdata`
--

CREATE TABLE `watchdogdata` (
  `time_utc` datetime NOT NULL,
  `time_local` datetime NOT NULL,
  `target1` float NOT NULL,
  `target2` float NOT NULL,
  `target3` float NOT NULL,
  `target4` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
