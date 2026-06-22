using System;
using System.Diagnostics;
using System.Text;
using System.Text.Json;
using System.Windows.Forms;

namespace OopsQl.SsmsGuard
{
    public sealed class OopsQlGuardCommand
    {
        public bool CanExecuteQuery(string sqlText)
        {
            var result = RunOopsQl(sqlText);
            if (result.ExitCode == 0)
            {
                return true;
            }

            using var document = JsonDocument.Parse(result.Output);
            var root = document.RootElement;
            var risk = root.GetProperty("overall_risk").GetString();
            var count = root.GetProperty("findings_count").GetInt32();

            var choice = MessageBox.Show(
                $"OopsQL found risky SQL before execution.\n\nOverall Risk: {risk}\nFindings: {count}\n\nCancel or run anyway?",
                "OopsQL warning",
                MessageBoxButtons.OKCancel,
                MessageBoxIcon.Warning
            );

            return choice == DialogResult.OK;
        }

        private static OopsQlResult RunOopsQl(string sqlText)
        {
            var startInfo = new ProcessStartInfo
            {
                FileName = "oopsql",
                Arguments = "scan-stdin --file ssms-query.sql --format json --fail-on HIGH",
                RedirectStandardInput = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8,
                StandardErrorEncoding = Encoding.UTF8
            };

            using var process = Process.Start(startInfo);
            if (process == null)
            {
                throw new InvalidOperationException("Could not start oopsql.");
            }

            process.StandardInput.Write(sqlText);
            process.StandardInput.Close();

            var output = process.StandardOutput.ReadToEnd();
            var error = process.StandardError.ReadToEnd();
            process.WaitForExit();

            return new OopsQlResult(process.ExitCode, string.IsNullOrWhiteSpace(output) ? error : output);
        }
    }

    public sealed record OopsQlResult(int ExitCode, string Output);
}

