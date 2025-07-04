using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SQLite;
using System.IO;
using System.Linq;
using System.Windows.Forms;

namespace Netra
{
    // Dataset model class
    public class Dataset
    {
        public int Id { get; set; }
        public string CompanyName { get; set; }
        public DateTime ScanDate { get; set; }
        public int TotalAssets { get; set; }
        public int ActiveAssets { get; set; }
        public string TopServices { get; set; }
        public int ScansProcessed { get; set; }
        public string RiskLevel { get; set; }
        public DateTime LastModified { get; set; }
        public string FileNotes { get; set; }
        public string OriginalFiles { get; set; }
        public DateTime CreatedDate { get; set; }
    }

    // Database manager class
    public class DatasetManager
    {
        private string connectionString;
        private string databasePath;

        public DatasetManager()
        {
            // Create database in application folder
            string appFolder = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "Netra");
            Directory.CreateDirectory(appFolder);
            databasePath = Path.Combine(appFolder, "datasets.db");
            connectionString = $"Data Source={databasePath};Version=3;";
            InitializeDatabase();
        }

        private void InitializeDatabase()
        {
            using (var connection = new SQLiteConnection(connectionString))
            {
                connection.Open();

                // Create Datasets table
                string createDatasetsTable = @"
                    CREATE TABLE IF NOT EXISTS Datasets (
                        Id INTEGER PRIMARY KEY AUTOINCREMENT,
                        CompanyName TEXT NOT NULL,
                        ScanDate TEXT NOT NULL,
                        TotalAssets INTEGER DEFAULT 0,
                        ActiveAssets INTEGER DEFAULT 0,
                        TopServices TEXT DEFAULT '',
                        ScansProcessed INTEGER DEFAULT 0,
                        RiskLevel TEXT DEFAULT '',
                        LastModified TEXT NOT NULL,
                        FileNotes TEXT DEFAULT '',
                        OriginalFiles TEXT DEFAULT '',
                        CreatedDate TEXT NOT NULL
                    )";

                // Create Assets table
                string createAssetsTable = @"
                    CREATE TABLE IF NOT EXISTS Assets (
                        Id INTEGER PRIMARY KEY AUTOINCREMENT,
                        DatasetId INTEGER,
                        IpAddress TEXT NOT NULL,
                        Hostname TEXT DEFAULT '',
                        Vendor TEXT DEFAULT '',
                        OpenPortCount INTEGER DEFAULT 0,
                        OpenServices TEXT DEFAULT '',
                        RawData TEXT DEFAULT '',
                        FOREIGN KEY (DatasetId) REFERENCES Datasets(Id) ON DELETE CASCADE
                    )";

                using (var command = new SQLiteCommand(createDatasetsTable, connection))
                {
                    command.ExecuteNonQuery();
                }

                using (var command = new SQLiteCommand(createAssetsTable, connection))
                {
                    command.ExecuteNonQuery();
                }
            }
        }

        // Helper method to safely get string from database reader
        private string GetSafeString(SQLiteDataReader reader, string columnName)
        {
            int ordinal = reader.GetOrdinal(columnName);
            return reader.IsDBNull(ordinal) ? "" : reader.GetString(ordinal);
        }

        // Helper method to safely get int from database reader
        private int GetSafeInt(SQLiteDataReader reader, string columnName)
        {
            int ordinal = reader.GetOrdinal(columnName);
            return reader.IsDBNull(ordinal) ? 0 : reader.GetInt32(ordinal);
        }

        // Helper method to safely get DateTime from database reader
        private DateTime GetSafeDateTime(SQLiteDataReader reader, string columnName, DateTime defaultValue = default)
        {
            int ordinal = reader.GetOrdinal(columnName);
            if (reader.IsDBNull(ordinal))
                return defaultValue == default ? DateTime.Now : defaultValue;

            string dateString = reader.GetString(ordinal);
            if (DateTime.TryParse(dateString, out DateTime result))
                return result;

            return defaultValue == default ? DateTime.Now : defaultValue;
        }

        public int SaveDataset(Dataset dataset, List<SimpleAsset> assets = null)
        {
            using (var connection = new SQLiteConnection(connectionString))
            {
                connection.Open();
                using (var transaction = connection.BeginTransaction())
                {
                    try
                    {
                        // Insert dataset
                        string insertDataset = @"
                            INSERT INTO Datasets (CompanyName, ScanDate, TotalAssets, ActiveAssets, TopServices, 
                                                 ScansProcessed, RiskLevel, LastModified, FileNotes, OriginalFiles, CreatedDate)
                            VALUES (@CompanyName, @ScanDate, @TotalAssets, @ActiveAssets, @TopServices, 
                                   @ScansProcessed, @RiskLevel, @LastModified, @FileNotes, @OriginalFiles, @CreatedDate)";

                        int datasetId;
                        using (var command = new SQLiteCommand(insertDataset, connection, transaction))
                        {
                            command.Parameters.AddWithValue("@CompanyName", dataset.CompanyName ?? "");
                            command.Parameters.AddWithValue("@ScanDate", dataset.ScanDate.ToString("yyyy-MM-dd"));
                            command.Parameters.AddWithValue("@TotalAssets", dataset.TotalAssets);
                            command.Parameters.AddWithValue("@ActiveAssets", dataset.ActiveAssets);
                            command.Parameters.AddWithValue("@TopServices", dataset.TopServices ?? "");
                            command.Parameters.AddWithValue("@ScansProcessed", dataset.ScansProcessed);
                            command.Parameters.AddWithValue("@RiskLevel", dataset.RiskLevel ?? "");
                            command.Parameters.AddWithValue("@LastModified", dataset.LastModified.ToString("yyyy-MM-dd HH:mm:ss"));
                            command.Parameters.AddWithValue("@FileNotes", dataset.FileNotes ?? "");
                            command.Parameters.AddWithValue("@OriginalFiles", dataset.OriginalFiles ?? "");
                            command.Parameters.AddWithValue("@CreatedDate", dataset.CreatedDate.ToString("yyyy-MM-dd HH:mm:ss"));

                            command.ExecuteNonQuery();
                            datasetId = (int)connection.LastInsertRowId;
                        }

                        // Insert assets if provided
                        if (assets != null && assets.Count > 0)
                        {
                            string insertAsset = @"
                                INSERT INTO Assets (DatasetId, IpAddress, Hostname, Vendor, OpenPortCount, OpenServices)
                                VALUES (@DatasetId, @IpAddress, @Hostname, @Vendor, @OpenPortCount, @OpenServices)";

                            foreach (var asset in assets)
                            {
                                using (var command = new SQLiteCommand(insertAsset, connection, transaction))
                                {
                                    command.Parameters.AddWithValue("@DatasetId", datasetId);
                                    command.Parameters.AddWithValue("@IpAddress", asset.IpAddress ?? "");
                                    command.Parameters.AddWithValue("@Hostname", asset.Hostname ?? "");
                                    command.Parameters.AddWithValue("@Vendor", asset.Vendor ?? "");
                                    command.Parameters.AddWithValue("@OpenPortCount", asset.OpenPortCount);
                                    command.Parameters.AddWithValue("@OpenServices", asset.OpenServices ?? "");
                                    command.ExecuteNonQuery();
                                }
                            }
                        }

                        transaction.Commit();
                        return datasetId;
                    }
                    catch
                    {
                        transaction.Rollback();
                        throw;
                    }
                }
            }
        }

        public List<Dataset> GetAllDatasets()
        {
            var datasets = new List<Dataset>();

            using (var connection = new SQLiteConnection(connectionString))
            {
                connection.Open();
                string query = "SELECT * FROM Datasets ORDER BY LastModified DESC";

                using (var command = new SQLiteCommand(query, connection))
                using (var reader = command.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        datasets.Add(new Dataset
                        {
                            Id = GetSafeInt(reader, "Id"),
                            CompanyName = GetSafeString(reader, "CompanyName"),
                            ScanDate = GetSafeDateTime(reader, "ScanDate"),
                            TotalAssets = GetSafeInt(reader, "TotalAssets"),
                            ActiveAssets = GetSafeInt(reader, "ActiveAssets"),
                            TopServices = GetSafeString(reader, "TopServices"),
                            ScansProcessed = GetSafeInt(reader, "ScansProcessed"),
                            RiskLevel = GetSafeString(reader, "RiskLevel"),
                            LastModified = GetSafeDateTime(reader, "LastModified"),
                            FileNotes = GetSafeString(reader, "FileNotes"),
                            OriginalFiles = GetSafeString(reader, "OriginalFiles"),
                            CreatedDate = GetSafeDateTime(reader, "CreatedDate")
                        });
                    }
                }
            }

            return datasets;
        }

        public Dataset GetDataset(int id)
        {
            using (var connection = new SQLiteConnection(connectionString))
            {
                connection.Open();
                string query = "SELECT * FROM Datasets WHERE Id = @Id";

                using (var command = new SQLiteCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@Id", id);
                    using (var reader = command.ExecuteReader())
                    {
                        if (reader.Read())
                        {
                            return new Dataset
                            {
                                Id = GetSafeInt(reader, "Id"),
                                CompanyName = GetSafeString(reader, "CompanyName"),
                                ScanDate = GetSafeDateTime(reader, "ScanDate"),
                                TotalAssets = GetSafeInt(reader, "TotalAssets"),
                                ActiveAssets = GetSafeInt(reader, "ActiveAssets"),
                                TopServices = GetSafeString(reader, "TopServices"),
                                ScansProcessed = GetSafeInt(reader, "ScansProcessed"),
                                RiskLevel = GetSafeString(reader, "RiskLevel"),
                                LastModified = GetSafeDateTime(reader, "LastModified"),
                                FileNotes = GetSafeString(reader, "FileNotes"),
                                OriginalFiles = GetSafeString(reader, "OriginalFiles"),
                                CreatedDate = GetSafeDateTime(reader, "CreatedDate")
                            };
                        }
                    }
                }
            }
            return null;
        }

        public List<SimpleAsset> GetDatasetAssets(int datasetId)
        {
            var assets = new List<SimpleAsset>();

            using (var connection = new SQLiteConnection(connectionString))
            {
                connection.Open();
                string query = "SELECT * FROM Assets WHERE DatasetId = @DatasetId";

                using (var command = new SQLiteCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@DatasetId", datasetId);
                    using (var reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            assets.Add(new SimpleAsset
                            {
                                IpAddress = GetSafeString(reader, "IpAddress"),
                                Hostname = GetSafeString(reader, "Hostname"),
                                Vendor = GetSafeString(reader, "Vendor"),
                                OpenPortCount = GetSafeInt(reader, "OpenPortCount"),
                                OpenServices = GetSafeString(reader, "OpenServices")
                            });
                        }
                    }
                }
            }

            return assets;
        }

        public void UpdateDataset(Dataset dataset)
        {
            using (var connection = new SQLiteConnection(connectionString))
            {
                connection.Open();
                string query = @"
                    UPDATE Datasets 
                    SET CompanyName = @CompanyName, ScanDate = @ScanDate, TotalAssets = @TotalAssets,
                        ActiveAssets = @ActiveAssets, TopServices = @TopServices, ScansProcessed = @ScansProcessed,
                        RiskLevel = @RiskLevel, LastModified = @LastModified, FileNotes = @FileNotes
                    WHERE Id = @Id";

                using (var command = new SQLiteCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@Id", dataset.Id);
                    command.Parameters.AddWithValue("@CompanyName", dataset.CompanyName ?? "");
                    command.Parameters.AddWithValue("@ScanDate", dataset.ScanDate.ToString("yyyy-MM-dd"));
                    command.Parameters.AddWithValue("@TotalAssets", dataset.TotalAssets);
                    command.Parameters.AddWithValue("@ActiveAssets", dataset.ActiveAssets);
                    command.Parameters.AddWithValue("@TopServices", dataset.TopServices ?? "");
                    command.Parameters.AddWithValue("@ScansProcessed", dataset.ScansProcessed);
                    command.Parameters.AddWithValue("@RiskLevel", dataset.RiskLevel ?? "");
                    command.Parameters.AddWithValue("@LastModified", DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"));
                    command.Parameters.AddWithValue("@FileNotes", dataset.FileNotes ?? "");
                    command.ExecuteNonQuery();
                }
            }
        }

        public void DeleteDataset(int id)
        {
            using (var connection = new SQLiteConnection(connectionString))
            {
                connection.Open();
                using (var transaction = connection.BeginTransaction())
                {
                    try
                    {
                        // Delete assets first (foreign key constraint)
                        string deleteAssets = "DELETE FROM Assets WHERE DatasetId = @Id";
                        using (var command = new SQLiteCommand(deleteAssets, connection, transaction))
                        {
                            command.Parameters.AddWithValue("@Id", id);
                            command.ExecuteNonQuery();
                        }

                        // Delete dataset
                        string deleteDataset = "DELETE FROM Datasets WHERE Id = @Id";
                        using (var command = new SQLiteCommand(deleteDataset, connection, transaction))
                        {
                            command.Parameters.AddWithValue("@Id", id);
                            command.ExecuteNonQuery();
                        }

                        transaction.Commit();
                    }
                    catch
                    {
                        transaction.Rollback();
                        throw;
                    }
                }
            }
        }

        public List<Dataset> SearchDatasets(string searchTerm)
        {
            var datasets = new List<Dataset>();

            using (var connection = new SQLiteConnection(connectionString))
            {
                connection.Open();
                string query = @"
                    SELECT * FROM Datasets 
                    WHERE CompanyName LIKE @SearchTerm 
                       OR TopServices LIKE @SearchTerm 
                       OR RiskLevel LIKE @SearchTerm
                       OR FileNotes LIKE @SearchTerm
                    ORDER BY LastModified DESC";

                using (var command = new SQLiteCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@SearchTerm", $"%{searchTerm}%");
                    using (var reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            datasets.Add(new Dataset
                            {
                                Id = GetSafeInt(reader, "Id"),
                                CompanyName = GetSafeString(reader, "CompanyName"),
                                ScanDate = GetSafeDateTime(reader, "ScanDate"),
                                TotalAssets = GetSafeInt(reader, "TotalAssets"),
                                ActiveAssets = GetSafeInt(reader, "ActiveAssets"),
                                TopServices = GetSafeString(reader, "TopServices"),
                                ScansProcessed = GetSafeInt(reader, "ScansProcessed"),
                                RiskLevel = GetSafeString(reader, "RiskLevel"),
                                LastModified = GetSafeDateTime(reader, "LastModified"),
                                FileNotes = GetSafeString(reader, "FileNotes"),
                                OriginalFiles = GetSafeString(reader, "OriginalFiles"),
                                CreatedDate = GetSafeDateTime(reader, "CreatedDate")
                            });
                        }
                    }
                }
            }

            return datasets;
        }
    }
}