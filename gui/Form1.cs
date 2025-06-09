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
                // Reset selection status
                label9.Text = "No Source Selected";
                label9.ForeColor = Color.Red;
            }
        }

        private void radioLibrarySource_CheckedChanged(object sender, EventArgs e)
        {
            if (radioLibrarySource.Checked)
            {
                btnSelectSource2.Text = "Select from Library";
                // Reset selection status
                label9.Text = "No Source Selected";
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
                MessageBox.Show("Library selection coming soon!", "Info");
                // Later: Open dataset library selection dialog
            }
        }
    }
}
