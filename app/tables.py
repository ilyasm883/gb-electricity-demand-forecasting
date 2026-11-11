# Small helpers that turn a table into markdown text, so the best values can be shown in bold.


# whole table, the row number in bold_row is written in bold
def markdown_table(df, bold_row):
    text = "| " + " | ".join(df.columns) + " |\n"
    text += "|" + "---|" * len(df.columns) + "\n"
    for i in range(len(df)):
        cells = [str(value) for value in df.iloc[i]]
        if i == bold_row:
            cells = ["**" + cell + "**" for cell in cells]
        text += "| " + " | ".join(cells) + " |\n"
    return text


# one row per group (for example weekday, weekend, holiday), the lowest error in each row is in bold
def best_in_row_table(df, first_column, model_names):
    text = "| " + first_column + " | Hours | " + " | ".join(model_names) + " |\n"
    text += "|" + "---|" * (len(model_names) + 2) + "\n"
    for i in range(len(df)):
        values = [round(df[name][i]) for name in model_names]
        best_value = min(values)
        cells = []
        for value in values:
            if value == best_value:
                cells.append("**" + str(value) + "**")
            else:
                cells.append(str(value))
        text += "| " + str(df.iloc[i, 0]) + " | " + str(df["hours"][i]) + " | " + " | ".join(cells) + " |\n"
    return text
