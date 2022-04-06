import pandas as pd
import xml.etree.ElementTree as ET
import json
import numpy as np


def write_QuickNII_XML(df: pd.DataFrame, filename: str, aligner: str) -> None:
    """
    Converts a pandas DataFrame to a quickNII compatible XML
    """
    df_temp = df.copy()
    if "nr" not in df_temp.columns:
        df_temp["nr"] = np.arange(len(df_temp)) + 1
    df_temp[["ox", "oy", "oz", "ux", "uy", "uz", "vx", "vy", "vz", "nr"]] = df[
        ["ox", "oy", "oz", "ux", "uy", "uz", "vx", "vy", "vz", "nr"]
    ].astype(str)
    out_df = pd.DataFrame(
        {
            "anchoring": "ox="
            + (df_temp.ox)
            + "&oy="
            + (df_temp.oy)
            + "&oz="
            + (df_temp.oz)
            + "&ux="
            + (df_temp.ux)
            + "&uy="
            + (df_temp.uy)
            + "&uz="
            + (df_temp.uz)
            + "&vx="
            + (df_temp.vx)
            + "&vy="
            + (df_temp.vy)
            + "&vz="
            + (df_temp.vz),
            "filename": df_temp.Filenames,
            "height": -999,
            "width": -999,
            "nr": df_temp.nr,
        }
    )
    print(f"saving to {filename}.xml")

    out_df.to_xml(
        filename + ".xml",
        index=False,
        root_name="series",
        row_name="slice",
        attr_cols=list(out_df.columns),
        namespaces={
            "first": df_temp.nr.values[0],
            "last": df_temp.nr.values[-1],
            "name": filename,
            "aligner": aligner,
            "": "",
        },
    )


def read_QuickNII_XML(filename: str) -> pd.DataFrame:
    """
    Converts a QuickNII XML to a pandas dataframe
    :param xml: The path to the QuickNII XML
    :type xml: str
    :return: A pandas dataframe
    :rtype: pd.DataFrame
    """
    df = pd.read_xml(filename)
    # split the anchoring string into separate columns
    anchoring = df.anchoring.str.split("&", expand=True).values
    # lambda function to remove non_numeric characters besides '.', we need this as all the 'ox=' etc is still in the strings
    strip = lambda x: "".join(
        c for c in x if c.isdigit() or c == "." or c == "-" or c == "e"
    )
    ##vectorise the lambda function and apply it to all elements
    anchoring = np.vectorize(strip)(anchoring)

    out_df = pd.DataFrame({"Filenames": df.filename})
    out_df[["ox", "oy", "oz", "ux", "uy", "uz", "vx", "vy", "vz"]] = anchoring
    return out_df


def write_QUINT_JSON(
    df: pd.DataFrame, filename: str, aligner: str, target: str
) -> None:
    """
    Converts a pandas DataFrame to a QUINT (QuickNII, Visualign, & Nutil) compatible JSON
    """
    if "nr" not in df.columns:
        df["nr"] = np.arange(len(df)) + 1
    alignments = df[["ox", "oy", "oz", "ux", "uy", "uz", "vx", "vy", "vz"]].values
    alignment_metadata = [
        {
            "filename": fn,
            "anchoring": list(alignment),
            "height": -999,
            "width": -999,
            "nr": nr,
        }
        for fn, alignment, nr in zip(df.Filenames, alignments, df.nr)
    ]
    QUINT_json = {
        "name": "",
        "target": target,
        "aligner": aligner,
        "slices": alignment_metadata,
    }
    print(f"saving to {filename}.json")
    with open(filename + ".json", "w") as f:
        json.dump(QUINT_json, f)
    with open(filename + ".json", "w") as outfile:
        json.dump(QUINT_json, outfile)


def read_QUINT_JSON(filename: str) -> pd.DataFrame:
    """
    Converts a QUINT JSON to a pandas dataframe
    :param json: The path to the QUINT JSON
    :type json: str
    :return: A pandas dataframe
    :rtype: pd.DataFrame
    """
    with open(filename, "r") as f:
        data = json.load(f)
    sections = data["slices"]
    target_volume = data["target"]
    alignments = [row["anchoring"] for row in sections]
    filenames = [row["filename"] for row in sections]
    section_numbers = [row["nr"] for row in sections]
    df = pd.DataFrame({"Filename": filenames, "nr": section_numbers})
    df[["ox", "oy", "oz", "ux", "uy", "uz", "vx", "vy", "vz"]] = alignments
    return df, target_volume
