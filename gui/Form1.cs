using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Diagnostics;

namespace Netra
{
    public partial class Form1 : Form
    {
        // Member variables for parser integration
        private List<string> selectedFiles = new List<string>();
        private List<SimpleAsset> parsedAssets = new List<SimpleAsset>();
        private DatasetManager datasetManager;
        private Form debugWindow;
        private TextBox debugTextBox;
        private bool debugMode = false;

        public Form1()
        {
            InitializeComponent();
            datasetManager = new DatasetManager();
            SetupDatasetLibrary();
        }

        private void SetupDatasetLibrary()
        {
            // Clear any existing columns
            dataGridView1.Columns.Clear();

            // Add columns in the correct order
            dataGridView1.Columns.Add("CompanyName", "Company Name");
            dataGridView1.Columns.Add("ScanDate", "Scan Date");
            dataGridView1.Columns.Add("FileNotes", "Notes");
            dataGridView1.Columns.Add("TotalAssets", "Total Assets");
            dataGridView1.Columns.Add("ActiveAssets", "Active Assets");
            dataGridView1.Columns.Add("AllServices", "All Services");
            dataGridView1.Columns.Add("ScansProcessed", "Scans Processed");
            dataGridView1.Columns.Add("RiskLevel", "Risk Level");
            dataGridView1.Columns.Add("LastModified", "Last Modified");

            // Add action buttons column
            DataGridViewButtonColumn actionsColumn = new DataGridViewButtonColumn();
            actionsColumn.Name = "Actions";
            actionsColumn.HeaderText = "Actions";
            actionsColumn.Text = "Select | View | Delete";
            actionsColumn.UseColumnTextForButtonValue = true;
            actionsColumn.Width = 150;
            dataGridView1.Columns.Add(actionsColumn);

            // Set column widths
            dataGridView1.Columns["CompanyName"].Width = 120;
            dataGridView1.Columns["ScanDate"].Width = 100;
            dataGridView1.Columns["FileNotes"].Width = 150;
            dataGridView1.Columns["TotalAssets"].Width = 80;
            dataGridView1.Columns["ActiveAssets"].Width = 80;
            dataGridView1.Columns["AllServices"].Width = 150;
            dataGridView1.Columns["ScansProcessed"].Width = 90;
            dataGridView1.Columns["RiskLevel"].Width = 80;
            dataGridView1.Columns["LastModified"].Width = 120;

            // Set grid properties
            dataGridView1.AllowUserToAddRows = false;
            dataGridView1.AllowUserToDeleteRows = false;
            dataGridView1.ReadOnly = true;
            dataGridView1.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
            dataGridView1.MultiSelect = false;

            // Wire up the event handler
            dataGridView1.CellContentClick += dataGridView1_CellContentClick;

            // Load actual data from database
            LoadDatasetLibrary();
        }

        private void LoadDatasetLibrary()
        {
            try
            {
                dataGridView1.Rows.Clear();
                var datasets = datasetManager.GetAllDatasets();

                foreach (var dataset in datasets)
                {
                    dataGridView1.Rows.Add(
                        dataset.CompanyName,
                        dataset.ScanDate.ToString("yyyy-MM-dd"),
                        dataset.FileNotes,
                        dataset.TotalAssets.ToString(),
                        dataset.ActiveAssets.ToString(),
                        dataset.AllServices,
                        dataset.ScansProcessed.ToString(),
                        dataset.RiskLevel,
                        dataset.LastModified.ToString("yyyy-MM-dd HH:mm"),
                        "Select | View | Delete"
                    );

                    // Store the dataset ID in the row tag for later reference
                    dataGridView1.Rows[dataGridView1.Rows.Count - 1].Tag = dataset.Id;
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading dataset library: {ex.Message}", "Database Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void TestDatabaseContents()
        {
            try
            {
                var datasets = datasetManager.GetAllDatasets();
                string message = $"Found {datasets.Count} datasets in database:\n\n";

                foreach (var dataset in datasets)
                {
                    message += $"ID: {dataset.Id}\n";
                    message += $"Company: {dataset.CompanyName}\n";
                    message += $"Date: {dataset.ScanDate}\n";
                    message += $"Files: {dataset.ScansProcessed}\n\n";
                }

                MessageBox.Show(message, "Database Contents");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error reading database: {ex.Message}", "Database Error");
            }
        }

        // Dataset Actions Methods
        private void ShowDatasetActions(int datasetId, string companyName, int rowIndex)
        {
            ContextMenuStrip actionMenu = new ContextMenuStrip();

            ToolStripMenuItem selectItem = new ToolStripMenuItem("Select for Report/Export");
            ToolStripMenuItem viewEditItem = new ToolStripMenuItem("View/Edit Dataset");
            ToolStripMenuItem deleteItem = new ToolStripMenuItem("Delete Dataset");

            selectItem.Click += (s, e) => SelectDataset(datasetId, companyName);
            viewEditItem.Click += (s, e) => ViewEditDataset(datasetId);
            deleteItem.Click += (s, e) => DeleteDataset(datasetId, companyName, rowIndex);

            actionMenu.Items.Add(selectItem);
            actionMenu.Items.Add(viewEditItem);
            actionMenu.Items.Add(new ToolStripSeparator());
            actionMenu.Items.Add(deleteItem);

            // Show the menu at the cursor position
            actionMenu.Show(Cursor.Position);
        }

        private void SelectDataset(int datasetId, string companyName)
        {
            try
            {
                var dataset = datasetManager.GetDataset(datasetId);

                string message = $"Selected dataset: {companyName}\n";
                message += $"Scan Date: {dataset.ScanDate:yyyy-MM-dd}\n";
                message += $"Total Assets: {dataset.TotalAssets}\n";
                message += $"Notes: {dataset.FileNotes}\n\n";
                message += "This dataset is now selected for report generation.";

                MessageBox.Show(message, "Dataset Selected", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error selecting dataset: {ex.Message}", "Selection Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void ViewEditDataset(int datasetId)
        {
            try
            {
                var dataset = datasetManager.GetDataset(datasetId);
                var assets = datasetManager.GetDatasetAssets(datasetId);

                string message = $"Dataset Details:\n\n";
                message += $"Company: {dataset.CompanyName}\n";
                message += $"Scan Date: {dataset.ScanDate:yyyy-MM-dd}\n";
                message += $"Notes: {dataset.FileNotes}\n";
                message += $"Files Processed: {dataset.ScansProcessed}\n";
                message += $"Total Assets: {dataset.TotalAssets}\n";
                message += $"Active Assets: {dataset.ActiveAssets}\n";
                message += $"All Services: {dataset.AllServices}\n";
                message += $"Risk Level: {dataset.RiskLevel}\n";
                message += $"Assets Found: {assets.Count}\n";
                message += $"Created: {dataset.CreatedDate:yyyy-MM-dd HH:mm}\n";
                message += $"Last Modified: {dataset.LastModified:yyyy-MM-dd HH:mm}";

                MessageBox.Show(message, "View Dataset", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading dataset: {ex.Message}", "View Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void DeleteDataset(int datasetId, string companyName, int rowIndex)
        {
            DialogResult result = MessageBox.Show(
                $"Are you sure you want to delete the dataset for {companyName}?\n\nThis action cannot be undone.",
                "Confirm Delete",
                MessageBoxButtons.YesNo,
                MessageBoxIcon.Warning);

            if (result == DialogResult.Yes)
            {
                try
                {
                    datasetManager.DeleteDataset(datasetId);
                    dataGridView1.Rows.RemoveAt(rowIndex);
                    MessageBox.Show("Dataset deleted successfully.", "Delete Complete", MessageBoxButtons.OK, MessageBoxIcon.Information);
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error deleting dataset: {ex.Message}", "Delete Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
        }

        // File Selection and Upload
        private void button1_Click(object sender, EventArgs e)
        {
            OpenFileDialog openFileDialog = new OpenFileDialog();
            openFileDialog.Filter = "Scan Files|*.zip;*.txt|All Files|*.*";
            openFileDialog.Title = "Select Scan Files";
            openFileDialog.Multiselect = true;

            if (openFileDialog.ShowDialog() == DialogResult.OK)
            {
                selectedFiles = openFileDialog.FileNames.ToList();

                List<string> validFiles = new List<string>();
                List<string> invalidFiles = new List<string>();

                foreach (string file in selectedFiles)
                {
                    string extension = Path.GetExtension(file).ToLower();
                    if (extension == ".zip" || extension == ".txt")
                    {
                        validFiles.Add(file);
                    }
                    else
                    {
                        invalidFiles.Add(file);
                    }
                }

                selectedFiles = validFiles;

                if (validFiles.Count == 1)
                {
                    textBox1.Text = validFiles[0];
                }
                else if (validFiles.Count > 1)
                {
                    textBox1.Text = $"{validFiles.Count} files selected";
                }

                if (invalidFiles.Count > 0 && validFiles.Count == 0)
                {
                    lblFileStatus.Text = "Invalid file types detected";
                    lblFileStatus.ForeColor = Color.Red;
                    textBox1.Text = "No valid files selected";
                }
                else if (invalidFiles.Count > 0 && validFiles.Count > 0)
                {
                    lblFileStatus.Text = $"{validFiles.Count} valid files, {invalidFiles.Count} ignored";
                    lblFileStatus.ForeColor = Color.Orange;
                }
                else if (validFiles.Count > 0)
                {
                    lblFileStatus.Text = $"{validFiles.Count} files ready to upload";
                    lblFileStatus.ForeColor = Color.Green;
                }
            }
            else
            {
                lblFileStatus.Text = "No files selected";
                lblFileStatus.ForeColor = Color.Red;
            }
        }

        private void button2_Click(object sender, EventArgs e)
        {
            if (selectedFiles.Count == 0)
            {
                MessageBox.Show("Please select files first!", "No Files Selected", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            bool parseAndReport = checkBox1.Checked;
            bool sendToScrubber = checkBox2.Checked;
            bool parseAndSaveToDatabase = checkBox3.Checked;

            if (!parseAndReport && !sendToScrubber && !parseAndSaveToDatabase)
            {
                MessageBox.Show("Please select at least one action!", "No Action Selected", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            if (parseAndReport || parseAndSaveToDatabase)
            {
                RunRealParserAndShowAssets();
            }
            else if (sendToScrubber)
            {
                MessageBox.Show("Send to Scrubber functionality will be implemented!", "Coming Soon", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }

        // Main Parser Execution
        private async void RunRealParserAndShowAssets()
        {
            try
            {
                if (debugMode) AddDebugMessage("=== STARTING PARSER ===");

                progressBar1.Visible = true;
                label2.Visible = true;
                label2.Text = "Initializing parser...";
                progressBar1.Value = 0;
                progressBar1.Maximum = 100;
                button2.Enabled = false;

                if (debugMode) AddDebugMessage($"Selected files: {selectedFiles.Count}");
                foreach (var file in selectedFiles)
                {
                    if (debugMode) AddDebugMessage($"File: {Path.GetFileName(file)} ({new FileInfo(file).Length:N0} bytes)");
                }

                await Task.Delay(50);
                progressBar1.Value = 5;
                Application.DoEvents();
                if (debugMode) AddDebugMessage("Initialization complete");

                label2.Text = "Parsing scan files...";
                progressBar1.Value = 10;
                Application.DoEvents();
                if (debugMode) AddDebugMessage("Starting Python parser...");

                string jsonOutput = await RunPythonParser(selectedFiles);

                if (debugMode) AddDebugMessage($"Python parser returned, JSON length: {jsonOutput?.Length ?? 0}");

                if (string.IsNullOrEmpty(jsonOutput))
                {
                    if (debugMode) AddDebugMessage("ERROR: JSON output is null or empty");
                    MessageBox.Show("Failed to parse scan files. Check debug window for details.", "Parse Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    ResetUploadUI();
                    return;
                }

                if (debugMode)
                {
                    string preview = jsonOutput.Length > 200 ? jsonOutput.Substring(0, 200) + "..." : jsonOutput;
                    AddDebugMessage($"JSON preview: {preview}");
                }

                label2.Text = "Processing results...";
                progressBar1.Value = 90;
                Application.DoEvents();
                if (debugMode) AddDebugMessage("Starting JSON parsing...");

                parsedAssets = ParseJsonResults(jsonOutput);
                if (debugMode) AddDebugMessage($"JSON parsing complete, found {parsedAssets.Count} assets");

                progressBar1.Value = 100;
                label2.Text = "Complete!";
                await Task.Delay(200);

                ResetUploadUI();
                if (debugMode) AddDebugMessage("UI reset complete");

                if (parsedAssets.Count == 0)
                {
                    if (debugMode) AddDebugMessage("WARNING: No assets found");
                    MessageBox.Show("No assets found in scan files. Check debug window for details.", "No Assets Found", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return;
                }

                if (debugMode) AddDebugMessage("Opening asset selection form...");
                ShowSimpleAssetSelection();
                if (debugMode) AddDebugMessage("=== PARSER COMPLETE ===");
            }
            catch (Exception ex)
            {
                if (debugMode) AddDebugMessage($"CRITICAL ERROR: {ex.Message}");
                if (debugMode) AddDebugMessage($"Stack trace: {ex.StackTrace}");
                MessageBox.Show($"Error during parsing: {ex.Message}\n\nCheck debug window for details.", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                ResetUploadUI();
            }
        }

        private void ResetUploadUI()
        {
            progressBar1.Visible = false;
            label2.Visible = false;
            button2.Enabled = true;
        }

        private async Task<string> RunPythonParser(List<string> filePaths)
        {
            try
            {
                if (debugMode) AddDebugMessage("=== STREAMLINED PARSER METHOD ===");

                string pythonExe = FindPythonExecutable();
                string pythonScript = Path.Combine(Application.StartupPath, "parser", "nmap_parser.py");

                if (debugMode) AddDebugMessage($"Python executable: {pythonExe}");
                if (debugMode) AddDebugMessage($"Parser script: {pythonScript}");

                if (!File.Exists(pythonScript))
                {
                    if (debugMode) AddDebugMessage("ERROR: Parser script not found!");
                    return null;
                }

                // ONLY use stdout method - skip the problematic export method entirely
                string arguments = $"\"{pythonScript}\" parse \"{filePaths[0]}\"";
                if (debugMode) AddDebugMessage($"Command: {pythonExe} {arguments}");

                return await RunSimplePythonCommand(pythonExe, arguments, 60000); // 60 second timeout
            }
            catch (Exception ex)
            {
                if (debugMode) AddDebugMessage($"EXCEPTION in RunPythonParser: {ex.Message}");
                return null;
            }
        }

        private async Task<string> RunSimplePythonCommand(string pythonExe, string arguments, int timeoutMs)
        {
            try
            {
                if (debugMode) AddDebugMessage($"Starting simple process: {pythonExe} {arguments}");

                Process process = new Process();
                process.StartInfo.FileName = pythonExe;
                process.StartInfo.Arguments = arguments;
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.RedirectStandardError = true;
                process.StartInfo.CreateNoWindow = true;
                process.StartInfo.WorkingDirectory = Path.GetDirectoryName(Path.Combine(Application.StartupPath, "parser", "nmap_parser.py"));

                StringBuilder allOutput = new StringBuilder();
                StringBuilder errorOutput = new StringBuilder();

                // Use simple synchronous reading for reliability
                process.Start();
                if (debugMode) AddDebugMessage($"Process started, PID: {process.Id}");

                // Start background tasks to read output
                var outputTask = Task.Run(() =>
                {
                    try
                    {
                        using (var reader = process.StandardOutput)
                        {
                            string line;
                            while ((line = reader.ReadLine()) != null)
                            {
                                allOutput.AppendLine(line);
                                if (debugMode) AddDebugMessage($"PYTHON OUT: {line}");
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        if (debugMode) AddDebugMessage($"Output reading error: {ex.Message}");
                    }
                });

                var errorTask = Task.Run(() =>
                {
                    try
                    {
                        using (var reader = process.StandardError)
                        {
                            string line;
                            while ((line = reader.ReadLine()) != null)
                            {
                                errorOutput.AppendLine(line);
                                if (debugMode) AddDebugMessage($"PYTHON ERR: {line}");
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        if (debugMode) AddDebugMessage($"Error reading error: {ex.Message}");
                    }
                });

                // Wait for process completion or timeout
                var processTask = Task.Run(() => process.WaitForExit());
                var completedTask = await Task.WhenAny(processTask, Task.Delay(timeoutMs));

                if (completedTask == processTask)
                {
                    // Process completed normally
                    if (debugMode) AddDebugMessage("Process completed normally");

                    // Wait for output tasks to complete
                    await Task.WhenAll(outputTask, errorTask);

                    if (debugMode) AddDebugMessage($"Process exit code: {process.ExitCode}");
                }
                else
                {
                    // Process timed out
                    if (debugMode) AddDebugMessage($"Process timed out after {timeoutMs}ms");
                    try { process.Kill(); } catch { }

                    // Give output tasks a chance to finish
                    await Task.Delay(2000);
                }

                process.Close();

                string stdout = allOutput.ToString().Trim();
                string stderr = errorOutput.ToString().Trim();

                if (debugMode) AddDebugMessage($"Final stdout length: {stdout.Length}");
                if (debugMode) AddDebugMessage($"Final stderr length: {stderr.Length}");

                // Check if we got asset data
                if (IsValidAssetOutput(stdout))
                {
                    if (debugMode) AddDebugMessage("Found valid asset output - extracting data");
                    return ExtractAssetsFromOutput(stdout);
                }

                // Return raw output if we got something
                if (!string.IsNullOrEmpty(stdout))
                {
                    if (debugMode) AddDebugMessage("Returning raw stdout");
                    return stdout;
                }

                if (!string.IsNullOrEmpty(stderr))
                {
                    if (debugMode) AddDebugMessage("Returning stderr");
                    return stderr;
                }

                if (debugMode) AddDebugMessage("No output received");
                return null;
            }
            catch (Exception ex)
            {
                if (debugMode) AddDebugMessage($"Exception in RunSimplePythonCommand: {ex.Message}");
                return null;
            }
        }

        // SIMPLIFIED validation method
        private bool IsValidAssetOutput(string output)
        {
            if (string.IsNullOrEmpty(output)) return false;

            // Look for any signs of asset data
            return output.Contains("] 172.16.") || // Asset entries
                   output.Contains("ALL ASSETS FOUND") || // Summary section
                   output.Contains("COMPLETE BREAKDOWN") || // Completion message
                   output.Contains("Processing complete!"); // Progress completion
        }

        private bool IsCompleteAssetOutput(string output)
        {
            // Multiple ways to detect complete output
            if (string.IsNullOrEmpty(output)) return false;

            // Method 1: Look for completion message
            if (output.Contains("COMPLETE BREAKDOWN FINISHED"))
            {
                if (debugMode) AddDebugMessage("Found 'COMPLETE BREAKDOWN FINISHED' marker");
                return true;
            }

            // Method 2: Look for the note about service uncertainty (always last message)
            if (output.Contains("couldn't confirm it with 100% certainty"))
            {
                if (debugMode) AddDebugMessage("Found final note about service uncertainty");
                return true;
            }

            // Method 3: Check for "Processing complete!" AND asset data
            if (output.Contains("Progress: 100% - Processing complete!") &&
                output.Contains("ALL ASSETS FOUND") &&
                output.Contains("] 172.16."))
            {
                if (debugMode) AddDebugMessage("Found processing complete with asset data");
                return true;
            }

            return false;
        }

        private string ExtractAssetsFromOutput(string output)
        {
            try
            {
                if (debugMode) AddDebugMessage("Starting simplified asset extraction...");

                var assets = new List<object>();
                var lines = output.Split('\n');

                object currentAsset = null;
                var services = new List<string>();

                foreach (var line in lines)
                {
                    var trimmed = line.Trim();

                    // Look for asset headers: [ 1] 172.16.1.1
                    var match = System.Text.RegularExpressions.Regex.Match(trimmed, @"\[\s*\d+\]\s+(\d+\.\d+\.\d+\.\d+)");
                    if (match.Success)
                    {
                        // Save previous asset
                        if (currentAsset != null)
                        {
                            var prev = (dynamic)currentAsset;
                            assets.Add(new
                            {
                                ip_address = prev.ip_address,
                                hostname = prev.hostname,
                                vendor = prev.vendor,
                                open_port_count = prev.open_port_count,
                                open_services = string.Join(", ", services)
                            });
                        }

                        // Start new asset
                        currentAsset = new
                        {
                            ip_address = match.Groups[1].Value,
                            hostname = "",
                            vendor = "Unknown",
                            open_port_count = 0
                        };
                        services.Clear();
                        continue;
                    }

                    // Parse asset details
                    if (currentAsset != null)
                    {
                        if (trimmed.StartsWith("Vendor:"))
                        {
                            var vendor = trimmed.Replace("Vendor:", "").Trim();
                            var asset = (dynamic)currentAsset;
                            currentAsset = new
                            {
                                ip_address = asset.ip_address,
                                hostname = asset.hostname,
                                vendor = vendor,
                                open_port_count = asset.open_port_count
                            };
                        }
                        else if (trimmed.StartsWith("Open Ports:"))
                        {
                            var portsStr = trimmed.Replace("Open Ports:", "").Trim();
                            if (int.TryParse(portsStr, out int ports))
                            {
                                var asset = (dynamic)currentAsset;
                                currentAsset = new
                                {
                                    ip_address = asset.ip_address,
                                    hostname = asset.hostname,
                                    vendor = asset.vendor,
                                    open_port_count = ports
                                };
                            }
                        }
                        else if (trimmed.Contains("- ") && trimmed.Contains(":"))
                        {
                            services.Add(trimmed.Replace("-", "").Trim());
                        }
                    }
                }

                // Don't forget the last asset
                if (currentAsset != null)
                {
                    var last = (dynamic)currentAsset;
                    assets.Add(new
                    {
                        ip_address = last.ip_address,
                        hostname = last.hostname,
                        vendor = last.vendor,
                        open_port_count = last.open_port_count,
                        open_services = string.Join(", ", services)
                    });
                }

                if (debugMode) AddDebugMessage($"Extracted {assets.Count} assets");

                // Build simple JSON
                var json = new StringBuilder();
                json.AppendLine("{");
                json.AppendLine("  \"summary\": {");
                json.AppendLine($"    \"total_devices\": {assets.Count},");
                json.AppendLine($"    \"active_devices\": {assets.Count},");
                json.AppendLine($"    \"total_open_ports\": {assets.Sum(a => ((dynamic)a).open_port_count)}");
                json.AppendLine("  },");
                json.AppendLine("  \"assets\": [");

                for (int i = 0; i < assets.Count; i++)
                {
                    var asset = (dynamic)assets[i];
                    json.AppendLine("    {");
                    json.AppendLine($"      \"ip_address\": \"{asset.ip_address}\",");
                    json.AppendLine($"      \"hostname\": \"{asset.hostname}\",");
                    json.AppendLine($"      \"vendor\": \"{asset.vendor}\",");
                    json.AppendLine($"      \"open_port_count\": {asset.open_port_count},");
                    json.AppendLine($"      \"open_services\": \"{asset.open_services}\"");
                    json.AppendLine(i < assets.Count - 1 ? "    }," : "    }");
                }

                json.AppendLine("  ]");
                json.AppendLine("}");

                return json.ToString();
            }
            catch (Exception ex)
            {
                if (debugMode) AddDebugMessage($"Extraction error: {ex.Message}");
                return "{\"summary\":{\"total_devices\":0,\"active_devices\":0,\"total_open_ports\":0},\"assets\":[]}";
            }
        }
        private void TestPythonOutputDirectly()
        {
            if (!debugMode)
            {
                MessageBox.Show("Please enable debug mode first.", "Debug Required");
                return;
            }

            try
            {
                if (selectedFiles.Count == 0)
                {
                    AddDebugMessage("No files selected for testing");
                    return;
                }

                string pythonExe = FindPythonExecutable();
                string pythonScript = Path.Combine(Application.StartupPath, "parser", "nmap_parser.py");
                string testFile = selectedFiles[0];

                AddDebugMessage("=== TESTING PYTHON OUTPUT DIRECTLY ===");
                AddDebugMessage($"Command: {pythonExe} \"{pythonScript}\" parse \"{testFile}\"");

                Process process = new Process();
                process.StartInfo.FileName = pythonExe;
                process.StartInfo.Arguments = $"\"{pythonScript}\" parse \"{testFile}\"";
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.RedirectStandardError = true;
                process.StartInfo.CreateNoWindow = true;

                process.Start();

                // Read all output at once
                string output = process.StandardOutput.ReadToEnd();
                string error = process.StandardError.ReadToEnd();

                process.WaitForExit(60000); // 60 second timeout

                AddDebugMessage($"Exit code: {process.ExitCode}");
                AddDebugMessage($"Output length: {output.Length}");
                AddDebugMessage($"Error length: {error.Length}");

                if (!string.IsNullOrEmpty(output))
                {
                    // Show first and last 500 chars to see structure
                    if (output.Length > 1000)
                    {
                        AddDebugMessage("FIRST 500 CHARS:");
                        AddDebugMessage(output.Substring(0, 500));
                        AddDebugMessage("LAST 500 CHARS:");
                        AddDebugMessage(output.Substring(output.Length - 500));
                    }
                    else
                    {
                        AddDebugMessage("FULL OUTPUT:");
                        AddDebugMessage(output);
                    }
                }

                if (!string.IsNullOrEmpty(error))
                {
                    AddDebugMessage("ERROR OUTPUT:");
                    AddDebugMessage(error);
                }

                process.Close();
                AddDebugMessage("=== DIRECT TEST COMPLETE ===");
            }
            catch (Exception ex)
            {
                AddDebugMessage($"Direct test failed: {ex.Message}");
            }
        }
        private void TestDirectPythonExecution()
        {
            if (!debugMode)
            {
                MessageBox.Show("Please enable debug mode first by checking 'Parse and Save Data to Database'", "Debug Required");
                return;
            }

            AddDebugMessage("=== TESTING DIRECT PYTHON EXECUTION ===");

            try
            {
                string pythonExe = FindPythonExecutable();
                string pythonScript = Path.Combine(Application.StartupPath, "parser", "nmap_parser.py");

                if (selectedFiles.Count == 0)
                {
                    AddDebugMessage("No files selected for testing");
                    return;
                }

                string testFile = selectedFiles[0];
                AddDebugMessage($"Testing with file: {Path.GetFileName(testFile)}");

                // Test 1: Basic script execution
                AddDebugMessage("Test 1: Basic script help");
                string helpArgs = $"\"{pythonScript}\" --help";

                Process helpProcess = new Process();
                helpProcess.StartInfo.FileName = pythonExe;
                helpProcess.StartInfo.Arguments = helpArgs;
                helpProcess.StartInfo.UseShellExecute = false;
                helpProcess.StartInfo.RedirectStandardOutput = true;
                helpProcess.StartInfo.RedirectStandardError = true;
                helpProcess.StartInfo.CreateNoWindow = true;

                helpProcess.Start();
                bool helpFinished = helpProcess.WaitForExit(5000);

                if (helpFinished)
                {
                    string helpOutput = helpProcess.StandardOutput.ReadToEnd();
                    AddDebugMessage($"Help command succeeded: {helpOutput.Length} chars");
                }
                else
                {
                    AddDebugMessage("Help command timed out");
                    try { helpProcess.Kill(); } catch { }
                }
                helpProcess.Close();

                // Test 2: File export with manual monitoring
                AddDebugMessage("Test 2: Export with manual monitoring");
                string tempFile = Path.Combine(Path.GetTempPath(), $"test_export_{DateTime.Now.Ticks}.json");
                string exportArgs = $"\"{pythonScript}\" parse --export \"{tempFile}\" \"{testFile}\"";

                Process exportProcess = new Process();
                exportProcess.StartInfo.FileName = pythonExe;
                exportProcess.StartInfo.Arguments = exportArgs;
                exportProcess.StartInfo.UseShellExecute = false;
                exportProcess.StartInfo.RedirectStandardOutput = true;
                exportProcess.StartInfo.RedirectStandardError = true;
                exportProcess.StartInfo.CreateNoWindow = true;

                var startTime = DateTime.Now;
                exportProcess.Start();

                // Monitor the process manually using Thread.Sleep
                for (int i = 0; i < 300; i++) // 30 seconds max, check every 100ms
                {
                    System.Threading.Thread.Sleep(100);

                    if (exportProcess.HasExited)
                    {
                        AddDebugMessage($"Process exited naturally after {(DateTime.Now - startTime).TotalMilliseconds}ms");
                        break;
                    }

                    // Check if file exists (script might be done even if process hasn't exited)
                    if (File.Exists(tempFile))
                    {
                        var fileInfo = new FileInfo(tempFile);
                        if (fileInfo.Length > 0)
                        {
                            AddDebugMessage($"Output file created after {(DateTime.Now - startTime).TotalMilliseconds}ms, size: {fileInfo.Length} bytes");

                            // Give it a bit more time to finish writing
                            System.Threading.Thread.Sleep(2000);

                            if (!exportProcess.HasExited)
                            {
                                AddDebugMessage("File created but process still running - forcing exit");
                                try { exportProcess.Kill(); } catch { }
                            }
                            break;
                        }
                    }
                }

                if (!exportProcess.HasExited)
                {
                    AddDebugMessage("Process did not exit after 30 seconds, killing it");
                    try { exportProcess.Kill(); } catch { }
                }

                // Check results
                if (File.Exists(tempFile))
                {
                    string content = File.ReadAllText(tempFile);
                    AddDebugMessage($"SUCCESS: Got {content.Length} characters from file");

                    try { File.Delete(tempFile); } catch { }

                    if (content.Contains("assets"))
                    {
                        AddDebugMessage("File contains asset data - this method works!");
                    }
                }
                else
                {
                    AddDebugMessage("No output file created");
                }

                exportProcess.Close();
                AddDebugMessage("=== DIRECT EXECUTION TEST COMPLETE ===");
            }
            catch (Exception ex)
            {
                AddDebugMessage($"Test failed: {ex.Message}");
            }
        }
        private void TestSimplePythonCall()
        {
            AddDebugMessage("=== TESTING SIMPLE PYTHON CALL ===");

            try
            {
                string pythonExe = FindPythonExecutable();
                AddDebugMessage($"Testing basic Python: {pythonExe} --version");

                Process process = new Process();
                process.StartInfo.FileName = pythonExe;
                process.StartInfo.Arguments = "--version";
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.RedirectStandardError = true;
                process.StartInfo.CreateNoWindow = true;

                process.Start();
                process.WaitForExit(5000);

                string output = process.StandardOutput.ReadToEnd();
                string error = process.StandardError.ReadToEnd();

                AddDebugMessage($"Python version output: {output}");
                if (!string.IsNullOrEmpty(error)) AddDebugMessage($"Python version error: {error}");

                // Test if the parser script exists and has basic syntax
                string pythonScript = Path.Combine(Application.StartupPath, "parser", "nmap_parser.py");
                AddDebugMessage($"Testing script syntax: {pythonExe} -m py_compile \"{pythonScript}\"");

                process = new Process();
                process.StartInfo.FileName = pythonExe;
                process.StartInfo.Arguments = $"-m py_compile \"{pythonScript}\"";
                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.RedirectStandardError = true;
                process.StartInfo.CreateNoWindow = true;

                process.Start();
                process.WaitForExit(5000);

                output = process.StandardOutput.ReadToEnd();
                error = process.StandardError.ReadToEnd();

                if (process.ExitCode == 0)
                {
                    AddDebugMessage("SUCCESS: Python script syntax is valid");
                }
                else
                {
                    AddDebugMessage($"ERROR: Python script has syntax errors:");
                    AddDebugMessage($"Output: {output}");
                    AddDebugMessage($"Error: {error}");
                }

                process.Close();
            }
            catch (Exception ex)
            {
                AddDebugMessage($"Error in simple Python test: {ex.Message}");
            }
        }

        private string FindPythonExecutable()
        {
            string bundledPython = Path.Combine(Application.StartupPath, "python", "python.exe");
            if (File.Exists(bundledPython))
                return bundledPython;

            // Try python3 first (to match Kali)
            try
            {
                var process = Process.Start(new ProcessStartInfo
                {
                    FileName = "python3",
                    Arguments = "--version",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    CreateNoWindow = true
                });

                if (process != null)
                {
                    process.WaitForExit();
                    if (process.ExitCode == 0)
                        return "python3";
                }
            }
            catch { }

            // Try regular python
            try
            {
                var process = Process.Start(new ProcessStartInfo
                {
                    FileName = "python",
                    Arguments = "--version",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    CreateNoWindow = true
                });

                if (process != null)
                {
                    process.WaitForExit();
                    if (process.ExitCode == 0)
                        return "python";
                }
            }
            catch { }

            throw new Exception("Python not found. Please install Python or contact support.");
        }

        private string ConvertTextOutputToJson(string textOutput)
        {
            try
            {
                if (debugMode) AddDebugMessage("Converting text output to JSON...");

                // Simple conversion without JSON library dependencies
                var ipMatches = System.Text.RegularExpressions.Regex.Matches(textOutput, @"\b(\d+\.\d+\.\d+\.\d+)\b");

                StringBuilder jsonBuilder = new StringBuilder();
                jsonBuilder.AppendLine("{");
                jsonBuilder.AppendLine("  \"summary\": {");
                jsonBuilder.AppendLine($"    \"total_devices\": {ipMatches.Count},");
                jsonBuilder.AppendLine($"    \"active_devices\": {ipMatches.Count},");
                jsonBuilder.AppendLine("    \"total_open_ports\": 0");
                jsonBuilder.AppendLine("  },");
                jsonBuilder.AppendLine("  \"assets\": [");

                for (int i = 0; i < ipMatches.Count; i++)
                {
                    string ip = ipMatches[i].Groups[1].Value;
                    jsonBuilder.AppendLine("    {");
                    jsonBuilder.AppendLine($"      \"ip_address\": \"{ip}\",");
                    jsonBuilder.AppendLine("      \"hostname\": \"\",");
                    jsonBuilder.AppendLine("      \"vendor\": \"Unknown\",");
                    jsonBuilder.AppendLine("      \"open_port_count\": 0,");
                    jsonBuilder.AppendLine("      \"open_services\": \"\"");

                    if (i < ipMatches.Count - 1)
                    {
                        jsonBuilder.AppendLine("    },");
                    }
                    else
                    {
                        jsonBuilder.AppendLine("    }");
                    }
                }

                jsonBuilder.AppendLine("  ]");
                jsonBuilder.AppendLine("}");

                if (debugMode) AddDebugMessage($"Extracted {ipMatches.Count} assets from text");

                return jsonBuilder.ToString();
            }
            catch (Exception ex)
            {
                if (debugMode) AddDebugMessage($"Error converting text to JSON: {ex.Message}");

                // Return minimal valid JSON if conversion fails
                return @"{
  ""summary"": {
    ""total_devices"": 0,
    ""active_devices"": 0,
    ""total_open_ports"": 0
  },
  ""assets"": [],
  ""error"": ""Failed to process output""
}";
            }
        }


        private List<SimpleAsset> ParseJsonResults(string jsonContent)
        {
            var assets = new List<SimpleAsset>();

            try
            {
                int assetsIndex = jsonContent.IndexOf("\"assets\":");
                if (assetsIndex == -1) return assets;

                int arrayStart = jsonContent.IndexOf("[", assetsIndex);
                if (arrayStart == -1) return assets;

                int bracketCount = 0;
                int arrayEnd = arrayStart;
                for (int i = arrayStart; i < jsonContent.Length; i++)
                {
                    if (jsonContent[i] == '[') bracketCount++;
                    if (jsonContent[i] == ']') bracketCount--;
                    if (bracketCount == 0)
                    {
                        arrayEnd = i;
                        break;
                    }
                }

                string assetsJson = jsonContent.Substring(arrayStart + 1, arrayEnd - arrayStart - 1);

                var assetMatches = System.Text.RegularExpressions.Regex.Matches(assetsJson, @"""ip_address"":\s*""([^""]+)""");
                var hostnameMatches = System.Text.RegularExpressions.Regex.Matches(assetsJson, @"""hostname"":\s*""([^""]*)""");
                var vendorMatches = System.Text.RegularExpressions.Regex.Matches(assetsJson, @"""vendor"":\s*""([^""]*)""");
                var portCountMatches = System.Text.RegularExpressions.Regex.Matches(assetsJson, @"""open_port_count"":\s*(\d+)");
                var servicesMatches = System.Text.RegularExpressions.Regex.Matches(assetsJson, @"""open_services"":\s*""([^""]*)""");

                for (int i = 0; i < assetMatches.Count; i++)
                {
                    var asset = new SimpleAsset
                    {
                        IpAddress = assetMatches[i].Groups[1].Value,
                        Hostname = i < hostnameMatches.Count ? hostnameMatches[i].Groups[1].Value : "",
                        Vendor = i < vendorMatches.Count ? vendorMatches[i].Groups[1].Value : "Unknown",
                        OpenPortCount = i < portCountMatches.Count ? int.Parse(portCountMatches[i].Groups[1].Value) : 0,
                        OpenServices = i < servicesMatches.Count ? servicesMatches[i].Groups[1].Value : "",
                        SelectedForReport = true
                    };

                    assets.Add(asset);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error parsing JSON results: {ex.Message}", "Parse Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }

            return assets;
        }

        private void ShowSimpleAssetSelection()
        {
            Form assetForm = new Form
            {
                Text = "Select Assets for Report",
                Size = new Size(900, 600),
                StartPosition = FormStartPosition.CenterParent
            };

            ListView listView = new ListView
            {
                View = View.Details,
                CheckBoxes = true,
                FullRowSelect = true,
                GridLines = true,
                Location = new Point(10, 10),
                Size = new Size(860, 450)
            };

            listView.Columns.Add("IP Address", 120);
            listView.Columns.Add("Hostname", 150);
            listView.Columns.Add("Vendor", 120);
            listView.Columns.Add("Open Ports", 80);
            listView.Columns.Add("Services", 370);

            foreach (var asset in parsedAssets)
            {
                ListViewItem item = new ListViewItem(asset.IpAddress);
                item.SubItems.Add(asset.Hostname ?? "");
                item.SubItems.Add(asset.Vendor ?? "Unknown");
                item.SubItems.Add(asset.OpenPortCount.ToString());
                item.SubItems.Add(asset.OpenServices ?? "");
                item.Checked = asset.SelectedForReport;
                item.Tag = asset;
                listView.Items.Add(item);
            }

            Button btnSave = new Button
            {
                Text = "Save to Database",
                Location = new Point(480, 520),
                Size = new Size(120, 35)
            };

            Button btnGenerateReport = new Button
            {
                Text = "Generate Report",
                Location = new Point(610, 520),
                Size = new Size(120, 35)
            };

            Button btnCancel = new Button
            {
                Text = "Cancel",
                Location = new Point(740, 520),
                Size = new Size(80, 35)
            };

            Label lblSummary = new Label
            {
                Text = $"Found {parsedAssets.Count} assets from scan files. Select assets to include.",
                Location = new Point(10, 480),
                Size = new Size(500, 40)
            };

            assetForm.Controls.Add(listView);
            assetForm.Controls.Add(btnSave);
            assetForm.Controls.Add(btnGenerateReport);
            assetForm.Controls.Add(btnCancel);
            assetForm.Controls.Add(lblSummary);

            btnSave.Click += (s, e) =>
            {
                var selectedAssets = new List<SimpleAsset>();
                foreach (ListViewItem item in listView.Items)
                {
                    if (item.Checked)
                    {
                        selectedAssets.Add((SimpleAsset)item.Tag);
                    }
                }

                if (selectedAssets.Count == 0)
                {
                    MessageBox.Show("Please select at least one asset to save.", "No Assets Selected", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return;
                }

                SaveParsedAssetsToDatabase(selectedAssets);
                MessageBox.Show($"Saved {selectedAssets.Count} assets to database successfully!", "Save Complete", MessageBoxButtons.OK, MessageBoxIcon.Information);
                assetForm.DialogResult = DialogResult.OK;
                assetForm.Close();
            };

            btnGenerateReport.Click += (s, e) =>
            {
                var selectedAssets = new List<SimpleAsset>();
                foreach (ListViewItem item in listView.Items)
                {
                    if (item.Checked)
                    {
                        selectedAssets.Add((SimpleAsset)item.Tag);
                    }
                }

                assetForm.DialogResult = DialogResult.OK;
                assetForm.Close();
                MessageBox.Show($"Selected {selectedAssets.Count} assets for report generation.\n\nReport generation functionality will be implemented next!", "Assets Selected", MessageBoxButtons.OK, MessageBoxIcon.Information);
            };

            btnCancel.Click += (s, e) =>
            {
                assetForm.DialogResult = DialogResult.Cancel;
                assetForm.Close();
            };

            assetForm.ShowDialog();
        }

        private void SaveParsedAssetsToDatabase(List<SimpleAsset> selectedAssets)
        {
            try
            {
                string companyName = textBox3.Text.Trim();
                DateTime scanDate = dateTimePicker1.Value;
                string fileNotes = textBox4.Text.Trim();

                if (string.IsNullOrEmpty(companyName))
                {
                    companyName = "Parsed Scan " + DateTime.Now.ToString("yyyy-MM-dd HH:mm");
                }

                if (fileNotes == "Enter scan types, Notes, Etc..." || fileNotes == "Enter scan types, notes, etc...")
                {
                    fileNotes = "";
                }

                var serviceCounts = new Dictionary<string, int>();
                var allServices = selectedAssets
                    .Where(asset => !string.IsNullOrEmpty(asset.OpenServices))
                    .SelectMany(asset => asset.OpenServices.Split(',', ';', '|'))
                    .Select(s => s.Trim())
                    .Where(s => !string.IsNullOrEmpty(s))
                    .ToList();

                foreach (var service in allServices)
                {
                    if (serviceCounts.ContainsKey(service))
                        serviceCounts[service]++;
                    else
                        serviceCounts[service] = 1;
                }

                string allServicesText = string.Join(", ", serviceCounts
                    .OrderByDescending(kvp => kvp.Value)
                    .Take(10)
                    .Select(kvp => kvp.Key));

                var dataset = new Dataset
                {
                    CompanyName = companyName,
                    ScanDate = scanDate,
                    TotalAssets = selectedAssets.Count,
                    ActiveAssets = selectedAssets.Count(a => a.OpenPortCount > 0),
                    AllServices = allServicesText,
                    ScansProcessed = selectedFiles.Count,
                    RiskLevel = "Run Report to Generate",
                    LastModified = DateTime.Now,
                    FileNotes = fileNotes,
                    OriginalFiles = string.Join(";", selectedFiles),
                    CreatedDate = DateTime.Now
                };

                int datasetId = datasetManager.SaveDataset(dataset, selectedAssets);
                MessageBox.Show($"Dataset with {selectedAssets.Count} assets saved to library!\nDataset ID: {datasetId}", "Parse & Save Complete", MessageBoxButtons.OK, MessageBoxIcon.Information);
                LoadDatasetLibrary();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error saving parsed assets to database: {ex.Message}", "Save Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        // DEBUG WINDOW FUNCTIONALITY
        private void checkBox3_CheckedChanged(object sender, EventArgs e)
        {
            if (checkBox3.Checked)
            {
                debugMode = true;
                OpenDebugWindow();
                AddDebugMessage("Debug mode enabled - ready to track parsing");
            }
            else
            {
                debugMode = false;
                if (debugWindow != null && !debugWindow.IsDisposed)
                {
                    debugWindow.Close();
                    debugWindow = null;
                }
            }
        }

        private void OpenDebugWindow()
        {
            try
            {
                if (debugWindow != null && !debugWindow.IsDisposed)
                {
                    debugWindow.Close();
                }

                debugWindow = new Form
                {
                    Text = "Parser Debug Output - RedBlue Labs",
                    Size = new Size(900, 700),
                    StartPosition = FormStartPosition.CenterScreen,
                    FormBorderStyle = FormBorderStyle.Sizable,
                    MinimumSize = new Size(600, 400)
                };

                Panel buttonPanel = new Panel
                {
                    Dock = DockStyle.Top,
                    Height = 40,
                    BackColor = Color.LightGray
                };

                Button clearBtn = new Button
                {
                    Text = "Clear Log",
                    Location = new Point(10, 8),
                    Size = new Size(80, 25)
                };

                Button saveBtn = new Button
                {
                    Text = "Save Log",
                    Location = new Point(100, 8),
                    Size = new Size(80, 25)
                };

                Button testBtn = new Button
                {
                    Text = "Test Parser",
                    Location = new Point(190, 8),
                    Size = new Size(100, 25)
                };

                clearBtn.Click += (s, e) => {
                    if (debugTextBox != null) debugTextBox.Clear();
                    AddDebugMessage("=== LOG CLEARED ===");
                };

                saveBtn.Click += (s, e) => SaveDebugLog();
                testBtn.Click += (s, e) => TestParserSetup();

                buttonPanel.Controls.AddRange(new Control[] { clearBtn, saveBtn, testBtn });

                debugTextBox = new TextBox
                {
                    Multiline = true,
                    ScrollBars = ScrollBars.Both,
                    ReadOnly = true,
                    Dock = DockStyle.Fill,
                    Font = new Font("Consolas", 9),
                    BackColor = Color.Black,
                    ForeColor = Color.LimeGreen,
                    WordWrap = false
                };

                debugWindow.Controls.Add(debugTextBox);
                debugWindow.Controls.Add(buttonPanel);

                debugWindow.FormClosing += (s, e) => {
                    debugMode = false;
                    checkBox3.Checked = false;
                };

                debugWindow.Show();

                AddDebugMessage("=== REDBLUE LABS PARSER DEBUG WINDOW ===");
                AddDebugMessage($"Debug session started at: {DateTime.Now}");
                AddDebugMessage($"Application path: {Application.StartupPath}");
                AddDebugMessage($"Current directory: {Environment.CurrentDirectory}");
                AddDebugMessage("=== READY FOR PARSING ===");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error opening debug window: {ex.Message}", "Debug Error");
            }
        }

        private void AddDebugMessage(string message)
        {
            try
            {
                if (debugTextBox != null && !debugTextBox.IsDisposed && debugTextBox.InvokeRequired)
                {
                    debugTextBox.Invoke((Action)(() => AppendDebugText(message)));
                }
                else if (debugTextBox != null && !debugTextBox.IsDisposed)
                {
                    AppendDebugText(message);
                }
            }
            catch (Exception)
            {
                // Silently handle debug errors
            }
        }

        private void AppendDebugText(string message)
        {
            try
            {
                string timestamp = DateTime.Now.ToString("HH:mm:ss.fff");
                string logLine = $"[{timestamp}] {message}\r\n";

                debugTextBox.AppendText(logLine);
                debugTextBox.SelectionStart = debugTextBox.Text.Length;
                debugTextBox.ScrollToCaret();

                if (debugTextBox.Lines.Length > 1000)
                {
                    var lines = debugTextBox.Lines;
                    var keepLines = lines.Skip(lines.Length - 800).ToArray();
                    debugTextBox.Lines = keepLines;
                }
            }
            catch (Exception)
            {
                // Silently handle debug errors
            }
        }

        private void SaveDebugLog()
        {
            try
            {
                SaveFileDialog saveDialog = new SaveFileDialog
                {
                    Filter = "Text Files (*.txt)|*.txt|All Files (*.*)|*.*",
                    FileName = $"parser_debug_log_{DateTime.Now:yyyyMMdd_HHmmss}.txt"
                };

                if (saveDialog.ShowDialog() == DialogResult.OK)
                {
                    File.WriteAllText(saveDialog.FileName, debugTextBox.Text);
                    AddDebugMessage($"Debug log saved to: {saveDialog.FileName}");
                }
            }
            catch (Exception ex)
            {
                AddDebugMessage($"Error saving log: {ex.Message}");
            }
        }

        private void TestParserSetup()
        {
            AddDebugMessage("=== TESTING PARSER SETUP ===");

            try
            {
                AddDebugMessage("Testing Python installation...");
                string pythonExe = FindPythonExecutable();
                AddDebugMessage($"SUCCESS: Python found at: {pythonExe}");

                string parserScript = Path.Combine(Application.StartupPath, "parser", "nmap_parser.py");
                AddDebugMessage($"Checking parser script: {parserScript}");
                AddDebugMessage($"Parser script exists: {File.Exists(parserScript)}");

                if (!File.Exists(parserScript))
                {
                    AddDebugMessage("ERROR: Parser script not found!");
                    AddDebugMessage($"Expected location: {parserScript}");
                    AddDebugMessage("Make sure the 'parser' folder with 'nmap_parser.py' is in your application directory");
                    return;
                }

                string scriptContent = File.ReadAllText(parserScript);
                AddDebugMessage($"SUCCESS: Parser script size: {scriptContent.Length:N0} characters");

                if (scriptContent.Contains("def main():") && scriptContent.Contains("parse"))
                {
                    AddDebugMessage("SUCCESS: Parser script appears to be valid");
                }
                else
                {
                    AddDebugMessage("WARNING: Parser script may be incomplete");
                }

                AddDebugMessage("Testing Python version...");
                ProcessStartInfo versionInfo = new ProcessStartInfo
                {
                    FileName = pythonExe,
                    Arguments = "--version",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                using (Process process = Process.Start(versionInfo))
                {
                    process.WaitForExit(5000);
                    string version = process.StandardOutput.ReadToEnd();
                    AddDebugMessage($"SUCCESS: Python version: {version.Trim()}");
                }

                AddDebugMessage("Testing parser script execution...");
                ProcessStartInfo helpInfo = new ProcessStartInfo
                {
                    FileName = pythonExe,
                    Arguments = $"\"{parserScript}\" --help",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                    WorkingDirectory = Path.GetDirectoryName(parserScript)
                };

                using (Process process = Process.Start(helpInfo))
                {
                    process.WaitForExit(10000);
                    string output = process.StandardOutput.ReadToEnd();
                    string error = process.StandardError.ReadToEnd();

                    AddDebugMessage($"Parser exit code: {process.ExitCode}");
                    AddDebugMessage($"Parser output length: {output.Length}");
                    AddDebugMessage($"Parser error length: {error.Length}");

                    if (process.ExitCode == 0 && output.Contains("parse"))
                    {
                        AddDebugMessage("SUCCESS: Parser script executes successfully");
                    }
                    else
                    {
                        AddDebugMessage($"PROBLEM: Parser script failed with exit code: {process.ExitCode}");
                        if (!string.IsNullOrEmpty(output))
                            AddDebugMessage($"Output: {output}");
                        if (!string.IsNullOrEmpty(error))
                            AddDebugMessage($"Error: {error}");
                    }
                }

                AddDebugMessage("=== PARSER SETUP TEST COMPLETE ===");
            }
            catch (Exception ex)
            {
                AddDebugMessage($"TEST FAILED: {ex.Message}");
                AddDebugMessage($"Stack trace: {ex.StackTrace}");
            }
        }

        // ALL THE EVENT HANDLERS
        private void label1_Click(object sender, EventArgs e) { }
        private void checkBox1_CheckedChanged(object sender, EventArgs e) { }
        private void pictureBox1_Click(object sender, EventArgs e) { }
        private void label2_Click(object sender, EventArgs e) { }
        private void panel1_Paint(object sender, PaintEventArgs e) { }
        private void panel1_Paint_1(object sender, PaintEventArgs e) { }
        private void tabPage1_Click(object sender, EventArgs e) { }
        private void label3_Click(object sender, EventArgs e) { }
        private void label4_Click(object sender, EventArgs e) { }
        private void pictureBox2_Click(object sender, EventArgs e) { }
        private void panel1_Paint_2(object sender, PaintEventArgs e) { }
        private void label4_Click_1(object sender, EventArgs e) { }

        private void textBox1_DragEnter(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                string[] files = (string[])e.Data.GetData(DataFormats.FileDrop);
                bool hasValidFile = false;
                foreach (string file in files)
                {
                    string extension = Path.GetExtension(file).ToLower();
                    if (extension == ".zip" || extension == ".txt")
                    {
                        hasValidFile = true;
                        break;
                    }
                }

                if (hasValidFile)
                {
                    e.Effect = DragDropEffects.Copy;
                }
                else
                {
                    e.Effect = DragDropEffects.None;
                }
            }
            else
            {
                e.Effect = DragDropEffects.None;
            }
        }

        private void textBox1_DragDrop(object sender, DragEventArgs e)
        {
            string[] droppedFiles = (string[])e.Data.GetData(DataFormats.FileDrop);
            selectedFiles = droppedFiles.ToList();

            List<string> validFiles = new List<string>();
            List<string> invalidFiles = new List<string>();

            foreach (string file in droppedFiles)
            {
                string extension = Path.GetExtension(file).ToLower();
                if (extension == ".zip" || extension == ".txt")
                {
                    validFiles.Add(file);
                }
                else
                {
                    invalidFiles.Add(file);
                }
            }

            selectedFiles = validFiles;

            if (validFiles.Count == 1)
            {
                textBox1.Text = validFiles[0];
            }
            else if (validFiles.Count > 1)
            {
                textBox1.Text = $"{validFiles.Count} files selected";
            }

            if (invalidFiles.Count > 0 && validFiles.Count == 0)
            {
                lblFileStatus.Text = "Invalid file types detected";
                lblFileStatus.ForeColor = Color.Red;
                textBox1.Text = "No valid files selected";
            }
            else if (invalidFiles.Count > 0 && validFiles.Count > 0)
            {
                lblFileStatus.Text = $"{validFiles.Count} valid files, {invalidFiles.Count} ignored";
                lblFileStatus.ForeColor = Color.Orange;
            }
            else if (validFiles.Count > 0)
            {
                lblFileStatus.Text = $"{validFiles.Count} files ready to upload";
                lblFileStatus.ForeColor = Color.Green;
            }
        }

        private void tabPage1_DragDrop(object sender, DragEventArgs e)
        {
            textBox1_DragDrop(sender, e);
        }

        private void tabPage1_DragEnter(object sender, DragEventArgs e)
        {
            textBox1_DragEnter(sender, e);
        }

        private void dataGridView1_CellContentClick(object sender, DataGridViewCellEventArgs e)
        {
            if (e.ColumnIndex == dataGridView1.Columns["Actions"].Index && e.RowIndex >= 0)
            {
                if (dataGridView1.Rows[e.RowIndex].Tag == null) return;

                int datasetId = (int)dataGridView1.Rows[e.RowIndex].Tag;
                string companyName = dataGridView1.Rows[e.RowIndex].Cells["CompanyName"].Value.ToString();

                ShowDatasetActions(datasetId, companyName, e.RowIndex);
            }
        }

        private void textBox3_TextChanged(object sender, EventArgs e) { }

        private void textBox4_Enter(object sender, EventArgs e)
        {
            if (textBox4.ForeColor == Color.DarkGray)
            {
                textBox4.Text = "";
                textBox4.ForeColor = Color.Black;
            }
        }

        private void textBox4_Leave(object sender, EventArgs e)
        {
            if (string.IsNullOrWhiteSpace(textBox4.Text))
            {
                textBox4.Text = "Enter scan types, notes, etc...";
                textBox4.ForeColor = Color.DarkGray;
            }
        }

        private void groupBox1_Enter(object sender, EventArgs e) { }
        private void checkBox4_CheckedChanged(object sender, EventArgs e) { }
        private void checkBox5_CheckedChanged(object sender, EventArgs e) { }
        private void checkBox6_CheckedChanged(object sender, EventArgs e) { }
        private void checkBox7_CheckedChanged(object sender, EventArgs e) { }
        private void label7_Enter(object sender, EventArgs e) { }

        private void textBox5_Enter(object sender, EventArgs e)
        {
            TextBox tb = sender as TextBox;
            if (tb.ForeColor == Color.DimGray)
            {
                tb.Text = "";
                tb.ForeColor = Color.Black;
            }
        }

        private void textBox5_Leave(object sender, EventArgs e)
        {
            TextBox tb = sender as TextBox;
            if (string.IsNullOrWhiteSpace(tb.Text))
            {
                tb.Text = "Enter company name, phone numbers, etc...";
                tb.ForeColor = Color.DimGray;
            }
        }

        private void textBox5_TextChanged(object sender, EventArgs e) { }
        private void textBox4_TextChanged(object sender, EventArgs e) { }
        private void radioButton1_CheckedChanged(object sender, EventArgs e) { }
        private void radioButton3_CheckedChanged(object sender, EventArgs e) { }
        private void radioButton2_CheckedChanged(object sender, EventArgs e) { }
        private void label8_Click(object sender, EventArgs e) { }
        private void groupBox3_Enter(object sender, EventArgs e) { }
        private void label8_Click_1(object sender, EventArgs e) { }

        private void radioFileSource_CheckedChanged(object sender, EventArgs e)
        {
            if (radioFileSource.Checked)
            {
                btnSelectSource2.Text = "Browse Files...";
                btnSelectSource2.Visible = true;
                label9.Text = "No Source Selected.";
                label9.ForeColor = Color.Red;
            }
        }

        private void radioLibrarySource_CheckedChanged(object sender, EventArgs e)
        {
            if (radioLibrarySource.Checked)
            {
                btnSelectSource2.Text = "Select from Library";
                btnSelectSource2.Visible = true;
                label9.Text = "No Source Selected.";
                label9.ForeColor = Color.Red;
            }
        }

        private void btnSelectSource2_Click(object sender, EventArgs e)
        {
            if (radioFileSource.Checked)
            {
                OpenFileDialog openFileDialog = new OpenFileDialog();
                openFileDialog.Filter = "Scan Files|*.zip;*.txt;*.nmap|All Files|*.*";
                openFileDialog.Title = "Select Scan File to Scrub";

                if (openFileDialog.ShowDialog() == DialogResult.OK)
                {
                    string fileName = Path.GetFileName(openFileDialog.FileName);
                    label9.Text = $"Selected: {fileName}";
                    label9.ForeColor = Color.Green;
                }
            }
            else if (radioLibrarySource.Checked)
            {
                MessageBox.Show("Dataset library selection will be implemented when the Dataset Library tab is complete!", "Coming Soon");
                label9.Text = "Selected: CLIENT-A Scan (June 5, 2025)";
                label9.ForeColor = Color.Green;
            }
            else
            {
                MessageBox.Show("Please select a data source type first!", "No Source Type Selected");
            }
        }

        private void SaveToLocal_CheckedChanged(object sender, EventArgs e)
        {
            buttonSaveLocal.Visible = SaveToLocal.Checked;
        }

        private void checkBox10_CheckedChanged(object sender, EventArgs e) { }
        private void checkBox11_CheckedChanged(object sender, EventArgs e) { }
        private void label11_Click(object sender, EventArgs e) { }
        private void label12_Click(object sender, EventArgs e) { }

        private void ScrubbingBtn_Click(object sender, EventArgs e)
        {
            if (label9.Text == "No Source Selected.")
            {
                MessageBox.Show("Please select a data source first!", "No Source Selected", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            bool hasOutput = checkBoxSaveToLibrary.Checked || SaveToLocal.Checked || checkBoxSendToReport.Checked;

            if (!hasOutput)
            {
                MessageBox.Show("Please select at least one output destination!", "No Output Selected", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            progressBarScrubbing.Visible = true;
            labelProcessing.Visible = true;
            ScrubbingBtn.Enabled = false;
            SimulateScrubbing();
        }

        private async void SimulateScrubbing()
        {
            try
            {
                progressBarScrubbing.Value = 0;
                progressBarScrubbing.Maximum = 100;

                labelProcessing.Text = "Reading source data...";
                for (int i = 0; i <= 30; i++)
                {
                    progressBarScrubbing.Value = i;
                    await Task.Delay(50);
                    Application.DoEvents();
                }

                labelProcessing.Text = "Applying scrubbing rules...";
                for (int i = 31; i <= 70; i++)
                {
                    progressBarScrubbing.Value = i;
                    await Task.Delay(40);
                    Application.DoEvents();
                }

                labelProcessing.Text = "Saving scrubbed data...";
                for (int i = 71; i <= 100; i++)
                {
                    progressBarScrubbing.Value = i;
                    await Task.Delay(30);
                    Application.DoEvents();
                }

                labelProcessing.Text = "Scrubbing complete!";

                string message = "Data scrubbing completed successfully!";
                if (checkBoxGenerateMapping.Checked)
                {
                    message += "\n\nMapping key has been generated.";
                }

                MessageBox.Show(message, "Success", MessageBoxButtons.OK, MessageBoxIcon.Information);

                progressBarScrubbing.Visible = false;
                labelProcessing.Visible = false;
                ScrubbingBtn.Enabled = true;

                label9.Text = "No Source Selected.";
                label9.ForeColor = Color.Red;
                radioFileSource.Checked = false;
                radioLibrarySource.Checked = false;
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error during scrubbing: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                ScrubbingBtn.Enabled = true;
                progressBarScrubbing.Visible = false;
                labelProcessing.Visible = false;
            }
        }

        private void checkBoxGenerateMapping_CheckedChanged(object sender, EventArgs e) { }

        private void buttonSaveLocal_Click(object sender, EventArgs e)
        {
            SaveFileDialog saveFileDialog = new SaveFileDialog();
            saveFileDialog.Filter = "Scrubbed Scan Files|*.zip;*.txt|All Files|*.*";
            saveFileDialog.Title = "Save Scrubbed Data As";
            saveFileDialog.DefaultExt = "zip";

            if (saveFileDialog.ShowDialog() == DialogResult.OK)
            {
                MessageBox.Show($"Will save to: {saveFileDialog.FileName}", "Save Location Set");
            }
        }

        private void LibrarySearch_TextChanged(object sender, EventArgs e)
        {
            string searchInput = LibrarySearch.Text.Trim();

            if (string.IsNullOrWhiteSpace(searchInput))
            {
                foreach (DataGridViewRow row in dataGridView1.Rows)
                {
                    row.Visible = true;
                }
                return;
            }

            string[] searchTerms = searchInput.Split(new char[] { ',' }, StringSplitOptions.RemoveEmptyEntries)
                .Select(term => term.Trim().ToLower())
                .ToArray();

            foreach (DataGridViewRow row in dataGridView1.Rows)
            {
                bool showRow = true;

                foreach (string searchTerm in searchTerms)
                {
                    bool termFound = false;

                    for (int i = 0; i < row.Cells.Count; i++)
                    {
                        if (row.Cells[i].Value != null)
                        {
                            string cellValue = row.Cells[i].Value.ToString().ToLower();
                            string[] words = cellValue.Split(new char[] { ' ', ',', '/', '|', '-' },
                                StringSplitOptions.RemoveEmptyEntries);

                            if (words.Any(word => word.Equals(searchTerm, StringComparison.OrdinalIgnoreCase)))
                            {
                                termFound = true;
                                break;
                            }
                        }
                    }

                    if (!termFound)
                    {
                        showRow = false;
                        break;
                    }
                }

                row.Visible = showRow;
            }
        }

        private void dataGridView1_CellContentClick_1(object sender, DataGridViewCellEventArgs e) { }

        private void button_Test_Click_Click(object sender, EventArgs e)
        {
            TestDatabaseContents();
        }
    }
}


// Simple data class for the parser integration
public class SimpleAsset
{
    public string IpAddress { get; set; }
    public string Hostname { get; set; }
    public string Vendor { get; set; }
    public int OpenPortCount { get; set; }
    public string OpenServices { get; set; }
    public bool SelectedForReport { get; set; } = true;
}