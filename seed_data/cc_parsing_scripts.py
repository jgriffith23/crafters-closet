"""A set of functions written to format seed data for Crafter's Closet
project."""


def create_sup_details_from_colors(read_filename, write_filename, sup_id, sup_type, brand, units):
    """Given a text file of only colors, create a list of supplies."""
    read_file_obj = open(read_filename)

    # Open in append mode
    write_file_obj = open(write_filename, "a")

    for line in read_file_obj:
        color = line.rstrip()
        data_row = ",".join([str(sup_id),
                            sup_type,
                            brand,
                            color.title(),
                            units,
                            "\n"])

        write_file_obj.write(data_row)
        sup_id += 1

    read_file_obj.close()
    write_file_obj.close()

    return sup_id


def create_red_heart_yarns(sup_id, filename):
    """"""
    read_file_obj = open("redheart.txt")
    write_file_obj = open(filename, "a")
    brand = "Red Heart"

    sup_type = "Yarn"
    units = "yds"

    for line in read_file_obj:
        line = line.rstrip()
        u_line = unicode(line, "utf-8")

        if not u_line.isnumeric():
            if line.upper() == line:
                brand = "Red Heart " + line.title()

            else:
                data_row = ",".join([str(sup_id),
                                     sup_type,
                                     brand,
                                     line.title(),
                                     units,
                                     "\n"])

                write_file_obj.write(data_row)
                sup_id += 1

    read_file_obj.close()
    write_file_obj.close()

sup_id = 0
new_id = create_sup_details_from_colors("americanacolors.txt",
                                        "paint_and_yarn.txt",
                                        sup_id,
                                        "Acrylic Paint",
                                        "Americana",
                                        "oz")

create_red_heart_yarns(new_id, "paint_and_yarn.txt")
