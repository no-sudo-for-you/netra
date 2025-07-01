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

        public Form1()
        {
            InitializeComponent();
            SetupDatasetLibrary();
        }

        private void SetupDatasetLibrary()
        {
            // Clear any existing columns
            dataGridView1.Columns.Clear();

            // Add columns
            dataGridView1.Columns.Add("CompanyName", "Company Name");
            dataGridView1.Columns.Add("ScanDate", "Scan Date");
            dataGridView1.Columns.Add("TotalAssets", "Total Assets");
            dataGridView1.Columns.Add("ActiveAssets", "Active Assets");
            dataGridView1.Columns.Add("TopServices", "Top Services");
            dataGridView1.Columns.Add("ScansProcessed", "Scans Processed");
            dataGridView1.Columns.Add("RiskLevel", "Risk Level");
            dataGridView1.Columns.Add("LastModified", "Last Modified");
            dataGridView1.Columns.Add("Actions", "Actions");

            // Set column widths
            dataGridView1.Columns["CompanyName"].Width = 120;
            dataGridView1.Columns["ScanDate"].Width = 100;
            dataGridView1.Columns["TotalAssets"].Width = 80;
            dataGridView1.Columns["ActiveAssets"].Width = 80;
            dataGridView1.Columns["TopServices"].Width = 150;
            dataGridView1.Columns["ScansProcessed"].Width = 90;
            dataGridView1.Columns["RiskLevel"].Width = 80;
            dataGridView1.Columns["LastModified"].Width = 120;
            dataGridView1.Columns["Actions"].Width = 100;

            // Set grid properties
            dataGridView1.AllowUserToAddRows = false;
            dataGridView1.AllowUserToDeleteRows = false;
            dataGridView1.ReadOnly = true;
            dataGridView1.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
            dataGridView1.MultiSelect = false;

            // Add sample data that matches your parser output
            AddSampleData();
        }

        private void AddSampleData()
        {
            // Sample data based on your nmap parser output format
            dataGridView1.Rows.Add("CLIENT-A", "2025-06-13", "10", "10", "http, ssh, ssl/https", "4", "", "2025-06-13 14:30", "View | Delete");
            dataGridView1.Rows.Add("CLIENT-B", "2025-06-12", "15", "12", "ssh, http, ftp", "3", "Medium", "2025-06-12 16:45", "View | Delete");
            dataGridView1.Rows.Add("CLIENT-C", "2025-06-10", "8", "8", "https, ssh, telnet", "2", "High", "2025-06-10 09:15", "View | Delete");
            dataGridView1.Rows.Add("ACME-CORP", "2025-06-08", "25", "23", "http, ssh, mysql", "6", "", "2025-06-08 11:20", "View | Delete");
            dataGridView1.Rows.Add("TECH-START", "2025-06-05", "6", "5", "ssh, http, wap-wsp", "2", "Low", "2025-06-05 13:10", "View | Delete");
        }

        private void label1_Click(object sender, EventArgs e)
        {

        }

        private void checkBox1_CheckedChanged(object sender, EventArgs e)
        {

        }

        private void button1_Click(object sender, EventArgs e)
        {
            // Create an OpenFileDialog to let user select files
            OpenFileDialog openFileDialog = new OpenFileDialog();

            // Set the file filter to only show .zip and .txt files
            openFileDialog.Filter = "Scan Files|*.zip;*.txt|All Files|*.*";
            openFileDialog.Title = "Select Scan Files";

            // Allow multiple file selection
            openFileDialog.Multiselect = true;

            // Show the dialog and check if user clicked OK
            if (openFileDialog.ShowDialog() == DialogResult.OK)
            {
                // Store selected files for parser integration
                selectedFiles = openFileDialog.FileNames.ToList();

                // Validate file types
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

                // Keep only valid files for parser
                selectedFiles = validFiles;

                // Update the textbox based on results
                if (validFiles.Count == 1)
                {
                    textBox1.Text = validFiles[0]; // Show single file path
                }
                else if (validFiles.Count > 1)
                {
                    textBox1.Text = $"{validFiles.Count} files selected"; // Show count for multiple files
                }

                // Update status label based on validation results
                if (invalidFiles.Count > 0 && validFiles.Count == 0)
                {
                    // All files are invalid
                    lblFileStatus.Text = "✗ Invalid file types detected";
                    lblFileStatus.ForeColor = Color.Red;
                    textBox1.Text = "No valid files selected";
                }
                else if (invalidFiles.Count > 0 && validFiles.Count > 0)
                {
                    // Some valid, some invalid
                    lblFileStatus.Text = $"⚠ {validFiles.Count} valid files, {invalidFiles.Count} ignored";
                    lblFileStatus.ForeColor = Color.Orange;
                }
                else if (validFiles.Count > 0)
                {
                    // All files are valid
                    lblFileStatus.Text = $"✓ {validFiles.Count} files ready to upload";
                    lblFileStatus.ForeColor = Color.Green;
                }
            }
            else
            {
                // User cancelled the dialog
                lblFileStatus.Text = "No files selected";
                lblFileStatus.ForeColor = Color.Red;
            }
        }

        private void button2_Click(object sender, EventArgs e)
        {
            // Check if user has selected files
            if (selectedFiles.Count == 0)
            {
                MessageBox.Show("Please select files first!", "No Files Selected", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            // Check what actions are selected
            bool parseAndReport = checkBox1.Checked; // Parse and Send to Report
            bool sendToScrubber = checkBox2.Checked; // Send to Scrubber  
            bool saveToDatabase = checkBox3.Checked; // Save Data to Database

            if (!parseAndReport && !sendToScrubber && !saveToDatabase)
            {
                MessageBox.Show("Please select at least one action!", "No Action Selected", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            if (parseAndReport)
            {
                // Run the REAL Python parser and show asset selection
                RunRealParserAndShowAssets();
            }
            else
            {
                // Keep your existing upload simulation for other actions
                progressBar1.Visible = true;
                label2.Visible = true;
                progressBar1.Value = 0;
                progressBar1.Maximum = 100;
                button2.Enabled = false;
                SimulateUpload();
            }
        }

        private async void RunRealParserAndShowAssets()
        {
            try
            {
                progressBar1.Visible = true;
                label2.Visible = true;
                label2.Text = "Running nmap parser...";
                progressBar1.Value = 0;
                button2.Enabled = false;

                // Phase 1: Setup
                for (int i = 0; i <= 20; i++)
                {
                    progressBar1.Value = i;
                    await Task.Delay(50);
                    Application.DoEvents();
                }

                // Phase 2: Run Python parser
                label2.Text = "Parsing scan files...";
                string jsonOutput = await RunPythonParser(selectedFiles);

                for (int i = 21; i <= 60; i++)
                {
                    progressBar1.Value = i;
                    await Task.Delay(30);
                    Application.DoEvents();
                }

                if (string.IsNullOrEmpty(jsonOutput))
                {
                    MessageBox.Show("Failed to parse scan files. Please check that Python is installed and the parser script is in the correct location.", "Parse Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    ResetUploadUI();
                    return;
                }

                // Phase 3: Parse JSON results
                label2.Text = "Processing results...";
                parsedAssets = ParseJsonResults(jsonOutput);

                for (int i = 61; i <= 100; i++)
                {
                    progressBar1.Value = i;
                    await Task.Delay(20);
                    Application.DoEvents();
                }

                ResetUploadUI();

                if (parsedAssets.Count == 0)
                {
                    MessageBox.Show("No assets found in scan files. Please check that the files contain valid nmap output.", "No Assets Found", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return;
                }

                // Show asset selection form
                ShowSimpleAssetSelection();

            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error during parsing: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
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
                // Create a temporary JSON file for output
                string tempOutputFile = Path.GetTempFileName() + ".json";
                string pythonScript = Path.Combine(Application.StartupPath, "parser", "nmap_parser.py");

                // Check if Python script exists
                if (!File.Exists(pythonScript))
                {
                    MessageBox.Show($"Python parser not found at: {pythonScript}\n\nPlease create a 'parser' folder in your application directory and copy nmap_parser.py into it.", "Parser Not Found", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    return null;
                }

                // Build command line arguments
                string arguments = $"parse --export \"{tempOutputFile}\"";
                foreach (string file in filePaths)
                {
                    arguments += $" \"{file}\"";
                }

                // Run Python script
                ProcessStartInfo startInfo = new ProcessStartInfo
                {
                    FileName = "python",
                    Arguments = $"\"{pythonScript}\" {arguments}",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                using (Process process = Process.Start(startInfo))
                {
                    await Task.Run(() => process.WaitForExit());

                    if (process.ExitCode != 0)
                    {
                        string error = process.StandardError.ReadToEnd();
                        string output = process.StandardOutput.ReadToEnd();
                        MessageBox.Show($"Python parser failed:\n\nError: {error}\n\nOutput: {output}\n\nMake sure Python is installed and accessible from command line.", "Parser Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                        return null;
                    }
                }

                // Read the JSON output
                if (File.Exists(tempOutputFile))
                {
                    string jsonContent = File.ReadAllText(tempOutputFile);
                    File.Delete(tempOutputFile); // Clean up
                    return jsonContent;
                }
                else
                {
                    MessageBox.Show("Parser did not generate output file.", "Parser Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    return null;
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error running Python parser: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return null;
            }
        }

        private List<SimpleAsset> ParseJsonResults(string jsonContent)
        {
            var assets = new List<SimpleAsset>();

            try
            {
                // Simple JSON parsing without external libraries
                // We'll extract the basic asset information

                // Look for the assets array in the JSON
                int assetsIndex = jsonContent.IndexOf("\"assets\":");
                if (assetsIndex == -1) return assets;

                // Find the start of the array
                int arrayStart = jsonContent.IndexOf("[", assetsIndex);
                if (arrayStart == -1) return assets;

                // Find the matching closing bracket
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

                // Split by asset objects (look for ip_address pattern)
                var assetMatches = System.Text.RegularExpressions.Regex.Matches(assetsJson, @"""ip_address"":\s*""([^""]+)""");
                var hostnameMatches = System.Text.RegularExpressions.Regex.Matches(assetsJson, @"""hostname"":\s*""([^""]*)""");
                var vendorMatches = System.Text.RegularExpressions.Regex.Matches(assetsJson, @"""vendor"":\s*""([^""]*)""");
                var portCountMatches = System.Text.RegularExpressions.Regex.Matches(assetsJson, @"""open_port_count"":\s*(\d+)");
                var servicesMatches = System.Text.RegularExpressions.Regex.Matches(assetsJson, @"""open_services"":\s*""([^""]*)""");

                // Create assets from the matches
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
            // Create a simple form to show the parsed assets
            Form assetForm = new Form
            {
                Text = "Select Assets for Report",
                Size = new Size(800, 500),
                StartPosition = FormStartPosition.CenterParent
            };

            // Create a ListView to show assets
            ListView listView = new ListView
            {
                View = View.Details,
                CheckBoxes = true,
                FullRowSelect = true,
                GridLines = true,
                Location = new Point(10, 10),
                Size = new Size(760, 350)
            };

            // Add columns
            listView.Columns.Add("IP Address", 120);
            listView.Columns.Add("Hostname", 150);
            listView.Columns.Add("Vendor", 120);
            listView.Columns.Add("Open Ports", 80);
            listView.Columns.Add("Services", 270);

            // Add assets to the list
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

            // Add buttons
            Button btnOk = new Button
            {
                Text = "Generate Report",
                Location = new Point(600, 380),
                Size = new Size(100, 30)
            };

            Button btnCancel = new Button
            {
                Text = "Cancel",
                Location = new Point(710, 380),
                Size = new Size(60, 30)
            };

            // Add summary label
            Label lblSummary = new Label
            {
                Text = $"Found {parsedAssets.Count} assets from scan files",
                Location = new Point(10, 385),
                Size = new Size(400, 20)
            };

            // Add controls to form
            assetForm.Controls.Add(listView);
            assetForm.Controls.Add(btnOk);
            assetForm.Controls.Add(btnCancel);
            assetForm.Controls.Add(lblSummary);

            // Event handlers
            btnOk.Click += (s, e) =>
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

                // Show confirmation
                MessageBox.Show($"Selected {selectedAssets.Count} assets for report generation.\n\nReport generation functionality will be implemented next!", "Assets Selected", MessageBoxButtons.OK, MessageBoxIcon.Information);
            };

            btnCancel.Click += (s, e) =>
            {
                assetForm.DialogResult = DialogResult.Cancel;
                assetForm.Close();
            };

            // Show the form
            assetForm.ShowDialog();
        }

        private async void SimulateUpload()
        {
            try
            {
                // Phase 1: Uploading files
                label2.Text = "Uploading files...";
                for (int i = 0; i <= 40; i++)
                {
                    progressBar1.Value = i;
                    await Task.Delay(50); // Simulate time
                    Application.DoEvents(); // Keep UI responsive
                }

                // Phase 2: Processing files
                label2.Text = "Processing scan data...";
                for (int i = 41; i <= 80; i++)
                {
                    progressBar1.Value = i;
                    await Task.Delay(30);
                    Application.DoEvents();
                }

                // Phase 3: Saving to database
                label2.Text = "Saving to database...";
                for (int i = 81; i <= 100; i++)
                {
                    progressBar1.Value = i;
                    await Task.Delay(40);
                    Application.DoEvents();
                }

                // Complete!
                label2.Text = "Upload complete!";
                MessageBox.Show("Files uploaded and processed successfully!", "Success", MessageBoxButtons.OK, MessageBoxIcon.Information);

                // Reset UI
                progressBar1.Visible = false;
                label2.Visible = false;
                button2.Enabled = true;
                textBox1.Text = "";
                lblFileStatus.Text = "No files selected";
                lblFileStatus.ForeColor = Color.Red;
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error during upload: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                button2.Enabled = true;
            }
        }

        private void pictureBox1_Click(object sender, EventArgs e)
        {

        }

        private void label2_Click(object sender, EventArgs e)
        {

        }

        private void panel1_Paint(object sender, PaintEventArgs e)
        {

        }

        private void panel1_Paint_1(object sender, PaintEventArgs e)
        {

        }

        private void tabPage1_Click(object sender, EventArgs e)
        {

        }

        private void label3_Click(object sender, EventArgs e)
        {

        }

        private void label4_Click(object sender, EventArgs e)
        {

        }

        private void pictureBox2_Click(object sender, EventArgs e)
        {

        }

        private void panel1_Paint_2(object sender, PaintEventArgs e)
        {

        }

        private void textBox1_DragEnter(object sender, DragEventArgs e)
        {
            // Check if the dragged data contains files
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                // Get the file paths
                string[] files = (string[])e.Data.GetData(DataFormats.FileDrop);

                // Check if at least one file has a valid extension
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

                // Allow drop if we have valid files
                if (hasValidFile)
                {
                    e.Effect = DragDropEffects.Copy; // Show "copy" cursor
                }
                else
                {
                    e.Effect = DragDropEffects.None; // Show "no drop" cursor
                }
            }
            else
            {
                e.Effect = DragDropEffects.None; // Not files, don't allow
            }
        }

        private void textBox1_DragDrop(object sender, DragEventArgs e)
        {
            // Get the dropped files
            string[] droppedFiles = (string[])e.Data.GetData(DataFormats.FileDrop);

            // Store selected files for parser integration
            selectedFiles = droppedFiles.ToList();

            // Validate file types (same logic as Browse button)
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

            // Keep only valid files for parser
            selectedFiles = validFiles;

            // Update the textbox based on results
            if (validFiles.Count == 1)
            {
                textBox1.Text = validFiles[0]; // Show single file path
            }
            else if (validFiles.Count > 1)
            {
                textBox1.Text = $"{validFiles.Count} files selected"; // Show count for multiple files
            }

            // Update status label based on validation results
            if (invalidFiles.Count > 0 && validFiles.Count == 0)
            {
                // All files are invalid
                lblFileStatus.Text = "✗ Invalid file types detected";
                lblFileStatus.ForeColor = Color.Red;
                textBox1.Text = "No valid files selected";
            }
            else if (invalidFiles.Count > 0 && validFiles.Count > 0)
            {
                // Some valid, some invalid
                lblFileStatus.Text = $"⚠ {validFiles.Count} valid files, {invalidFiles.Count} ignored";
                lblFileStatus.ForeColor = Color.Orange;
            }
            else if (validFiles.Count > 0)
            {
                // All files are valid
                lblFileStatus.Text = $"✓ {validFiles.Count} files ready to upload";
                lblFileStatus.ForeColor = Color.Green;
            }
        }

        private void tabPage1_DragDrop(object sender, DragEventArgs e)
        {
            // Get the dropped files
            string[] droppedFiles = (string[])e.Data.GetData(DataFormats.FileDrop);

            // Store selected files for parser integration
            selectedFiles = droppedFiles.ToList();

            // Validate file types (same logic as Browse button)
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

            // Keep only valid files for parser
            selectedFiles = validFiles;

            // Update the textbox based on results
            if (validFiles.Count == 1)
            {
                textBox1.Text = validFiles[0]; // Show single file path
            }
            else if (validFiles.Count > 1)
            {
                textBox1.Text = $"{validFiles.Count} files selected"; // Show count for multiple files
            }

            // Update status label based on validation results
            if (invalidFiles.Count > 0 && validFiles.Count == 0)
            {
                // All files are invalid
                lblFileStatus.Text = "✗ Invalid file types detected";
                lblFileStatus.ForeColor = Color.Red;
                textBox1.Text = "No valid files selected";
            }
            else if (invalidFiles.Count > 0 && validFiles.Count > 0)
            {
                // Some valid, some invalid
                lblFileStatus.Text = $"⚠ {validFiles.Count} valid files, {invalidFiles.Count} ignored";
                lblFileStatus.ForeColor = Color.Orange;
            }
            else if (validFiles.Count > 0)
            {
                // All files are valid
                lblFileStatus.Text = $"✓ {validFiles.Count} files ready to upload";
                lblFileStatus.ForeColor = Color.Green;
            }
        }

        private void tabPage1_DragEnter(object sender, DragEventArgs e)
        {
            // Check if the dragged data contains files
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                // Get the file paths
                string[] files = (string[])e.Data.GetData(DataFormats.FileDrop);

                // Check if at least one file has a valid extension
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

                // Allow drop if we have valid files
                if (hasValidFile)
                {
                    e.Effect = DragDropEffects.Copy; // Show "copy" cursor
                }
                else
                {
                    e.Effect = DragDropEffects.None; // Show "no drop" cursor
                }
            }
            else
            {
                e.Effect = DragDropEffects.None; // Not files, don't allow
            }
        }

        private void label4_Click_1(object sender, EventArgs e)
        {

        }

        private void dataGridView1_CellContentClick(object sender, DataGridViewCellEventArgs e)
        {

        }

        private void textBox3_TextChanged(object sender, EventArgs e)
        {

        }

        private void textBox4_Enter(object sender, EventArgs e)
        {
            if (textBox4.ForeColor == Color.DarkGray) // If it's still placeholder color
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

        private void groupBox1_Enter(object sender, EventArgs e)
        {

        }

        private void checkBox4_CheckedChanged(object sender, EventArgs e)
        {

        }

        private void checkBox5_CheckedChanged(object sender, EventArgs e)
        {

        }

        private void checkBox6_CheckedChanged(object sender, EventArgs e)
        {

        }

        private void checkBox7_CheckedChanged(object sender, EventArgs e)
        {

        }

        private void label7_Enter(object sender, EventArgs e)
        {

        }

        private void textBox5_Enter(object sender, EventArgs e)
        {
            TextBox tb = sender as TextBox;
            if (tb.ForeColor == Color.DimGray) // If it's still placeholder color
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

        private void textBox5_TextChanged(object sender, EventArgs e)
        {

        }

        private void textBox4_TextChanged(object sender, EventArgs e)
        {

        }

        private void radioButton1_CheckedChanged(object sender, EventArgs e)
        {

        }

        private void radioButton3_CheckedChanged(object sender, EventArgs e)
        {

        }

        private void radioButton2_CheckedChanged(object sender, EventArgs e)
        {

        }

        private void label8_Click(object sender, EventArgs e)
        {

        }

        private void groupBox3_Enter(object sender, EventArgs e)
        {

        }

        private void label8_Click_1(object sender, EventArgs e)
        {

        }

        private void radioFileSource_CheckedChanged(object sender, EventArgs e)
        {
            if (radioFileSource.Checked)
            {
                btnSelectSource2.Text = "Browse Files...";
                btnSelectSource2.Visible = true; // Show browse button

                // Reset selection status
                label9.Text = "No Source Selected.";
                label9.ForeColor = Color.Red;
            }
        }

        private void radioLibrarySource_CheckedChanged(object sender, EventArgs e)
        {
            if (radioLibrarySource.Checked)
            {
                btnSelectSource2.Text = "Select from Library";
                btnSelectSource2.Visible = true; // Show browse button

                // Reset selection status
                label9.Text = "No Source Selected.";
                label9.ForeColor = Color.Red;
            }
        }

        private void btnSelectSource2_Click(object sender, EventArgs e)
        {
            if (radioFileSource.Checked)
            {
                // File selection logic
                OpenFileDialog openFileDialog = new OpenFileDialog();
                openFileDialog.Filter = "Scan Files|*.zip;*.txt;*.nmap|All Files|*.*";
                openFileDialog.Title = "Select Scan File to Scrub";

                if (openFileDialog.ShowDialog() == DialogResult.OK)
                {
                    // File selected successfully
                    string fileName = Path.GetFileName(openFileDialog.FileName);
                    label9.Text = $"Selected: {fileName}";
                    label9.ForeColor = Color.Green;
                }
            }
            else if (radioLibrarySource.Checked)
            {
                // Library selection logic (placeholder for now)
                MessageBox.Show("Dataset library selection will be implemented when the Dataset Library tab is complete!", "Coming Soon");

                // For demo purposes, simulate selecting from library
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
            // Show/hide the browse button based on checkbox state
            buttonSaveLocal.Visible = SaveToLocal.Checked;
        }

        private void checkBox10_CheckedChanged(object sender, EventArgs e)
        {

        }

        private void checkBox11_CheckedChanged(object sender, EventArgs e)
        {

        }

        private void label11_Click(object sender, EventArgs e)
        {

        }

        private void label12_Click(object sender, EventArgs e)
        {

        }

        private void ScrubbingBtn_Click(object sender, EventArgs e)
        {
            // Check if user has selected a source
            if (label9.Text == "No Source Selected.")
            {
                MessageBox.Show("Please select a data source first!", "No Source Selected", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            // Check if at least one output destination is selected
            bool hasOutput = checkBoxSaveToLibrary.Checked || SaveToLocal.Checked || checkBoxSendToReport.Checked;

            if (!hasOutput)
            {
                MessageBox.Show("Please select at least one output destination!", "No Output Selected", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            // Show progress elements
            progressBarScrubbing.Visible = true;
            labelProcessing.Visible = true;

            // Disable the button during processing
            ScrubbingBtn.Enabled = false;

            // Start the scrubbing simulation
            SimulateScrubbing();
        }

        private async void SimulateScrubbing()
        {
            try
            {
                // Reset progress
                progressBarScrubbing.Value = 0;
                progressBarScrubbing.Maximum = 100;

                // Phase 1: Reading source data
                labelProcessing.Text = "Reading source data...";
                for (int i = 0; i <= 30; i++)
                {
                    progressBarScrubbing.Value = i;
                    await Task.Delay(50);
                    Application.DoEvents();
                }

                // Phase 2: Applying scrubbing rules
                labelProcessing.Text = "Applying scrubbing rules...";
                for (int i = 31; i <= 70; i++)
                {
                    progressBarScrubbing.Value = i;
                    await Task.Delay(40);
                    Application.DoEvents();
                }

                // Phase 3: Saving outputs
                labelProcessing.Text = "Saving scrubbed data...";
                for (int i = 71; i <= 100; i++)
                {
                    progressBarScrubbing.Value = i;
                    await Task.Delay(30);
                    Application.DoEvents();
                }

                // Complete!
                labelProcessing.Text = "Scrubbing complete!";

                // Generate mapping key if requested
                string message = "Data scrubbing completed successfully!";
                if (checkBoxGenerateMapping.Checked)
                {
                    message += "\n\nMapping key has been generated.";
                }

                MessageBox.Show(message, "Success", MessageBoxButtons.OK, MessageBoxIcon.Information);

                // Reset UI
                progressBarScrubbing.Visible = false;
                labelProcessing.Visible = false;
                ScrubbingBtn.Enabled = true;

                // Reset source selection
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

        private void checkBoxGenerateMapping_CheckedChanged(object sender, EventArgs e)
        {

        }

        private void buttonSaveLocal_Click(object sender, EventArgs e)
        {
            SaveFileDialog saveFileDialog = new SaveFileDialog();
            saveFileDialog.Filter = "Scrubbed Scan Files|*.zip;*.txt|All Files|*.*";
            saveFileDialog.Title = "Save Scrubbed Data As";
            saveFileDialog.DefaultExt = "zip";

            if (saveFileDialog.ShowDialog() == DialogResult.OK)
            {
                // Store the selected path (we'll use this when actually saving)
                // For now, just show confirmation
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
                bool showRow = true; // Start with true, must match ALL terms

                // Check that ALL search terms are found
                foreach (string searchTerm in searchTerms)
                {
                    bool termFound = false;

                    // Check each cell in the row for this specific term
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

                    // If this term wasn't found, hide the row
                    if (!termFound)
                    {
                        showRow = false;
                        break;
                    }
                }

                row.Visible = showRow;
            }
        }

        private void dataGridView1_CellContentClick_1(object sender, DataGridViewCellEventArgs e)
        {

        }
    }
}

// Simple data classes for the parser integration
public class SimpleAsset
{
    public string IpAddress { get; set; }
    public string Hostname { get; set; }
    public string Vendor { get; set; }
    public int OpenPortCount { get; set; }
    public string OpenServices { get; set; }
    public bool SelectedForReport { get; set; } = true;
}