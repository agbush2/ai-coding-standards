# PowerShell Testing Standards
Implementation of: /testing_standards.md

## Framework
- **Tool**: Pester 5+.
- **Scope**: Unit tests for all Public/Private functions. Integration tests for module workflow.

## Structure
- **Location**: `/tests` folder at the root, mimicking the `/src` structure.
- **Naming**: `filename.Tests.ps1`.

## Pester Guidelines
- **Describe/Context**: Use `Describe` for the command, `Context` for the scenario.
- **It**: Use `It` for assertions.
- **Mocking**: Use `Mock` to isolate units from external systems (File system, AD, API).
- **Assertions**: Use `Should` syntax (e.g., `Should -Be`, `Should -Throw`).

## Code Coverage
- **Metric**: Aim for 80%+ code coverage on logic-heavy functions.
- **Tools**: Use `Invoke-Pester -CodeCoverage` to generate reports.

## Coverage Reporting
- **Threshold**: Minimum 80% code coverage required for PR approval.
- **Reporting Tools**: Integrate with Coveralls or Codecov for CI reporting if possible.

## Example
```powershell
Describe 'Get-MyWidget' {
    Context 'When widget exists' {
        Mock Get-Item { return @{ Name = 'TestWidget' } }

        It 'Returns the correct widget name' {
            $result = Get-MyWidget -Name 'TestWidget'
            $result.Name | Should -Be 'TestWidget'
        }
    }
}
```
