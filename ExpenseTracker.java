import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.awt.event.*;
import java.util.ArrayList;

public class ExpenseTracker extends JFrame {
    private DefaultTableModel incomeModel, expenseModel;
    private JLabel balanceLabel;
    private java.util.List<Integer> incomes = new ArrayList<>();
    private java.util.List<Integer> expenses = new ArrayList<>();

    public ExpenseTracker() {
        setTitle("Expense Tracker");
        setSize(800, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());

        // ===== Top Panel (Buttons) =====
        JPanel topPanel = new JPanel();
        JButton addIncomeBtn = new JButton("Add Income");
        JButton addExpenseBtn = new JButton("Add Expense");
        JButton deleteBtn = new JButton("Delete Selected");
        topPanel.add(addIncomeBtn);
        topPanel.add(addExpenseBtn);
        topPanel.add(deleteBtn);

        // ===== Tables =====
        incomeModel = new DefaultTableModel(new String[]{"Source", "Amount"}, 0);
        expenseModel = new DefaultTableModel(new String[]{"Category", "Amount"}, 0);

        JTable incomeTable = new JTable(incomeModel);
        JTable expenseTable = new JTable(expenseModel);

        JSplitPane splitPane = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT,
                new JScrollPane(incomeTable), new JScrollPane(expenseTable));
        splitPane.setDividerLocation(380);

        // ===== Balance Label =====
        balanceLabel = new JLabel("Balance: 0", JLabel.CENTER);
        balanceLabel.setFont(new Font("Arial", Font.BOLD, 18));
        balanceLabel.setBorder(BorderFactory.createEmptyBorder(10, 0, 10, 0));

        // ===== Chart Panel =====
        JPanel chartPanel = new JPanel() {
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                int totalIncome = incomes.stream().mapToInt(i -> i).sum();
                int totalExpense = expenses.stream().mapToInt(i -> i).sum();
                int total = totalIncome + totalExpense;
                if (total == 0) return;

                int incomeAngle = (int) Math.round(360.0 * totalIncome / total);
                int expenseAngle = 360 - incomeAngle;

                g.setColor(new Color(41, 128, 185)); // blue income
                g.fillArc(150, 20, 200, 200, 0, incomeAngle);

                g.setColor(new Color(192, 57, 43)); // red expense
                g.fillArc(150, 20, 200, 200, incomeAngle, expenseAngle);

                g.setColor(Color.BLACK);
                g.drawString("Income", 370, 100);
                g.setColor(new Color(41, 128, 185));
                g.fillRect(420, 90, 20, 20);

                g.setColor(Color.BLACK);
                g.drawString("Expense", 370, 140);
                g.setColor(new Color(192, 57, 43));
                g.fillRect(420, 130, 20, 20);
            }
        };
        chartPanel.setPreferredSize(new Dimension(600, 250));

        // ===== Add to Frame =====
        add(topPanel, BorderLayout.NORTH);
        add(splitPane, BorderLayout.CENTER);
        add(balanceLabel, BorderLayout.SOUTH);
        add(chartPanel, BorderLayout.EAST);

        // ===== Actions =====
        addIncomeBtn.addActionListener(e -> {
            String source = JOptionPane.showInputDialog(this, "Enter Income Source:");
            String amtStr = JOptionPane.showInputDialog(this, "Enter Amount:");
            try {
                int amt = Integer.parseInt(amtStr);
                incomeModel.addRow(new Object[]{source, amt});
                incomes.add(amt);
                updateBalance();
                chartPanel.repaint();
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Invalid amount!");
            }
        });

        addExpenseBtn.addActionListener(e -> {
            String cat = JOptionPane.showInputDialog(this, "Enter Expense Category:");
            String amtStr = JOptionPane.showInputDialog(this, "Enter Amount:");
            try {
                int amt = Integer.parseInt(amtStr);
                expenseModel.addRow(new Object[]{cat, amt});
                expenses.add(amt);
                updateBalance();
                chartPanel.repaint();
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Invalid amount!");
            }
        });

        deleteBtn.addActionListener(e -> {
            int incRow = incomeTable.getSelectedRow();
            int expRow = expenseTable.getSelectedRow();
            if (incRow != -1) {
                int amt = (int) incomeModel.getValueAt(incRow, 1);
                incomes.remove(Integer.valueOf(amt));
                incomeModel.removeRow(incRow);
            } else if (expRow != -1) {
                int amt = (int) expenseModel.getValueAt(expRow, 1);
                expenses.remove(Integer.valueOf(amt));
                expenseModel.removeRow(expRow);
            }
            updateBalance();
            chartPanel.repaint();
        });

        setVisible(true);
    }

    private void updateBalance() {
        int totalIncome = incomes.stream().mapToInt(i -> i).sum();
        int totalExpense = expenses.stream().mapToInt(i -> i).sum();
        balanceLabel.setText("Balance: " + (totalIncome - totalExpense));
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(ExpenseTracker::new);
    }
}
