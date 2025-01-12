import streamlit as st
import datetime
import plotly.graph_objects as go


# Define the BudgetTracker class
class BudgetTracker:
    def __init__(self):
        self.income = 0
        self.expenses = []
        self.categories = ["Rent", "Food", "Entertainment", "Transportation", "Miscellaneous"]

    def add_income(self, amount):
        self.income += amount

    def add_expense(self, amount, category):
        if category not in self.categories:
            return False
        self.expenses.append({"amount": amount, "category": category, "date": datetime.datetime.now()})
        return True

    def view_expenses(self):
        return self.expenses

    def get_total_expenses(self):
        return sum(expense['amount'] for expense in self.expenses)

    def get_remaining_budget(self):
        total_expenses = self.get_total_expenses()
        return self.income - total_expenses

    def view_spending_by_category(self):
        spending_by_category = {category: 0 for category in self.categories}
        for expense in self.expenses:
            spending_by_category[expense['category']] += expense['amount']
        return spending_by_category

    def spending_insights(self):
        total_expenses = self.get_total_expenses()
        remaining_budget = self.get_remaining_budget()

        insights = {"total_income": self.income, "total_expenses": total_expenses, "remaining_budget": remaining_budget}

        if total_expenses > self.income:
            insights["message"] = "⚠️ Warning: You are overspending! Try to cut down on unnecessary expenses."
            insights["status"] = "warning"
        elif total_expenses > self.income * 0.8:
            insights["message"] = "⚠️ Caution: You are nearing your budget limit. Consider saving more."
            insights["status"] = "caution"
        else:
            insights["message"] = "🎉 Great job! You are managing your budget well."
            insights["status"] = "success"

        return insights


# Initialize the BudgetTracker instance in session state
if 'tracker' not in st.session_state:
    st.session_state.tracker = BudgetTracker()

tracker = st.session_state.tracker

# Streamlit interface code
st.set_page_config(page_title="Budget Tracker App", layout="centered")
st.title("💰 Budget Tracker App")

# Layout: Use columns to organize the main progress bars
col1, col2 = st.columns(2)

with col1:
    # Income Circular Progress
    income = tracker.income
    income_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=income,
        title={'text': "Total Income"},
        gauge={
            'axis': {'range': [0, max(income, 1000)]},
            'bar': {'color': "#00CC96"},
            'steps': [
                {'range': [0, income], 'color': "#E0F7FA"}
            ],
        }
    ))
    income_fig.update_layout(width=300, height=250)
    st.plotly_chart(income_fig, use_container_width=True)

with col2:
    # Remaining Budget Circular Progress
    remaining = tracker.get_remaining_budget()
    remaining_percentage = (remaining / tracker.income * 100) if tracker.income else 0
    remaining_percentage = max(min(remaining_percentage, 100), 0)  # Clamp between 0 and 100

    remaining_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=remaining,
        title={'text': "Remaining Budget"},
        gauge={
            'axis': {'range': [0, max(tracker.income, 1000)]},
            'bar': {'color': "#FF9900"},
            'steps': [
                {'range': [0, tracker.income], 'color': "#FFF2CC"}
            ],
        }
    ))
    remaining_fig.update_layout(width=300, height=250)
    st.plotly_chart(remaining_fig, use_container_width=True)

# Add Income Section
st.header("➕ Add Income")
income_input = st.number_input("Enter income amount: $", min_value=0.0, step=100.0, format="%.2f")
if st.button("Add Income"):
    tracker.add_income(income_input)
    st.success(f"✅ Income of ${income_input:.2f} added. Total income is now ${tracker.income:.2f}.")

# Add Expense Section
st.header("➖ Add Expense")
expense_amount = st.number_input("Enter expense amount: $", min_value=0.0, step=10.0, format="%.2f",
                                 key="expense_amount")
category = st.selectbox("Choose a category", tracker.categories)
if st.button("Add Expense"):
    if tracker.add_expense(expense_amount, category):
        st.success(f"✅ Expense of ${expense_amount:.2f} added under {category}.")
    else:
        st.error("❌ Invalid category!")

# View Expenses Section
st.header("📜 View Expenses")
if st.button("Show Expenses"):
    expenses = tracker.view_expenses()
    if expenses:
        for expense in expenses:
            st.write(
                f"• **${expense['amount']:.2f}** - {expense['category']} on {expense['date'].strftime('%Y-%m-%d')}")
    else:
        st.write("No expenses recorded.")

# View Remaining Budget Section
st.header("📊 View Remaining Budget")
if st.button("Show Remaining Budget"):
    remaining_budget = tracker.get_remaining_budget()
    st.write(f"**Your remaining budget is:** ${remaining_budget:.2f}")

# Spending Insights Section
st.header("🔍 Spending Insights")
if st.button("Show Spending Insights"):
    insights = tracker.spending_insights()
    st.write(f"**Total Income:** ${insights['total_income']:.2f}")
    st.write(f"**Total Expenses:** ${insights['total_expenses']:.2f}")
    st.write(f"**Remaining Budget:** ${insights['remaining_budget']:.2f}")

    # Display styled message based on status
    if insights["status"] == "warning":
        st.error(insights["message"])
    elif insights["status"] == "caution":
        st.warning(insights["message"])
    else:
        st.success(insights["message"])

    # Display spending by category as circular charts
    st.subheader("💸 Spending by Category")
    categories = tracker.view_spending_by_category()
    total_expenses = tracker.get_total_expenses()

    if total_expenses > 0:
        for cat, amt in categories.items():
            if amt > 0:
                cat_percentage = (amt / total_expenses) * 100
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=amt,
                    title={'text': f"{cat} ({cat_percentage:.1f}%)"},
                    gauge={
                        'axis': {'range': [0, max(categories.values())]},
                        'bar': {'color': "#FFA500"},
                        'steps': [
                            {'range': [0, amt], 'color': "#FFE5B4"}
                        ],
                    }
                ))
                fig.update_layout(width=250, height=200, margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No expenses to display.")

# Optional: Hide Streamlit's default menu and footer for a cleaner look
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
