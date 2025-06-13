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


namespace Netra
{
    public partial class Form1 : Form
    {
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
                // Get all selected file paths
                string[] selectedFiles = openFileDialog.FileNames;

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
            if (string.IsNullOrEmpty(textBox1.Text))
            {
                MessageBox.Show("Please select files first!", "No Files Selected", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            // Show the progress bar and status label
            progressBar1.Visible = true;
            label2.Visible = true;

            // Reset progress bar
            progressBar1.Value = 0;
            progressBar1.Maximum = 100;

            // Disable the upload button during processing
            button2.Enabled = false;

            // Start the upload simulation
            SimulateUpload();
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
    }
}
