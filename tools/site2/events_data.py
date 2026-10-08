"""New school/college products and the 8 event categories (48 events)."""
import os
EX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'extra')
STAMP = '2026-10-09T09:00:00.000Z'

# (file, name, subcategory, description, moq, occasions)
SCHOOL = [
    ('28-product-9.jpg', 'Little Explorer Gift Chest', 'Kids Hampers', 'A keepsake box packed with an astronaut desk clock, sipper, stationery and goodies, ready to personalise with the child\'s name.', 10, ['birthday']),
    ('51TVOcKGdvL._AC_UF1000,1000_QL80_.jpg', 'Christmas Stationery Gift Box', 'Stationery Kits', 'A bright Christmas-themed stationery set in a window gift box: pencils, eraser, sharpener, ruler and more.', 25, []),
    ('51WZbnBCyUL.jpg', "Children's Day Printed Mug", 'Mugs & Keepsakes', "A white ceramic mug printed with a cheerful Children's Day design. Add each child's name or the school logo.", 25, ['birthday']),
    ('61RCMSlcO8L._AC_UF1000,1000_QL80_.jpg', 'Christmas Stationery Kit Duo', 'Stationery Kits', 'Two-colour festive stationery kits that make an easy Christmas return gift for a whole class.', 25, []),
    ('711R2jXWmwL._AC_UF1000,1000_QL80_.jpg', 'Space Explorer Stationery Tote', 'Stationery Kits', 'A space-themed tote bag filled with pencils, stickers, a notebook, keychain and a UV-light pen.', 20, ['birthday']),
    ('71PaAgg5NmL._AC_UF1000,1000_QL80_.jpg', 'Astronaut Stationery Set with Tote', 'Stationery Kits', 'An astronaut pencil box, crayons, ruler, keychain and notebook packed in a matching printed tote.', 20, ['birthday']),
    ('815+X12jPyL._AC_UF1000,1000_QL80_.jpg', 'Merry Christmas Stationery Combo', 'Stationery Kits', 'A Christmas pencil box with pencils, colours and accessories, gift-ready for school celebrations.', 25, []),
    ('81I8pistsoL._AC_UF1000,1000_QL80_.jpg', 'Classroom Return Gift Mega Pack', 'Return Gifts', 'A bulk pack for a whole class: pens, pencils, erasers, illusion books, bendy pencils and dino toys.', 1, ['birthday']),
    ('81fPkUpxUwL._AC_UF1000,1000_QL80_.jpg', 'Cartoon Pencil & Eraser Set', 'Return Gifts', 'Pencil, eraser, sharpener and ruler on a fun cartoon card. A budget favourite for Children\'s Day.', 50, ['birthday']),
    ('Childrens-Day-gifts.png', 'Unicorn Pastel Stationery Box', 'Stationery Kits', 'Pastel pencils, a unicorn notebook and stationery in a printed gift box.', 20, ['birthday']),
    ('b6bbf753cb578b6485352a45653c0b9b.jpg', 'Welcome Back Crayon Caddy', 'Return Gifts', 'A kraft caddy with crayons, scissors, glue and a pencil flag, labelled with each child\'s name.', 25, []),
    ('best backpack on childrens day.jpg', 'Animal Mini Backpack', 'Bags & Bottles', 'Soft unicorn and zebra mini backpacks for little ones. Embroider or print the school name.', 20, ['birthday']),
    ('image7-1.jpg', 'Class Yearbook & Memory Book', 'Mugs & Keepsakes', 'A hardbound yearbook or annual-day memory book with your class photos, printed in-house.', 30, ['farewell']),
    ('images (1).jfif', 'Art Kit Gift Tray', 'Kids Hampers', 'A gift tray with an art kit, colours, sketch pens and stationery from trusted kids\' brands.', 10, ['birthday']),
    ('images (2).jfif', 'Astronaut Pencil Box Set', 'Stationery Kits', 'An astronaut pencil box, pens, crayons and a space tote. A big hit for Children\'s Day.', 20, ['birthday']),
    ('images (3).jfif', 'Space Theme Birthday Hamper', 'Kids Hampers', 'A personalised space-theme hamper with a diary, rocket bottle, pencils and toys.', 10, ['birthday']),
    ('images (4).jfif', 'Crayon Cone Return Gifts', 'Return Gifts', 'Crayon bundles wrapped in kraft cones with a name tag. Cheap, cheerful and quick to make.', 50, ['birthday']),
    ('images (5).jfif', 'Smiley Cup Crayon Favours', 'Return Gifts', 'Smiley-face cups filled with crayons and treats, wrapped and ribboned.', 50, ['birthday']),
    ('images (6).jfif', 'Candy Cup Party Favours', 'Return Gifts', 'Clear cups with lollipops, candies and a mini toy for school parties.', 50, ['birthday']),
    ('images (7).jfif', 'Pencil & Eraser Return Gift Packs', 'Return Gifts', 'Individually packed pencil and eraser sets with a "Thank you" tag for every student.', 50, []),
    ('images.jfif', 'Art & Treat Gift Basket', 'Kids Hampers', 'A basket of art supplies, colours and chocolates for prize winners and special days.', 10, ['birthday']),
    ('kids-theme-jute-party-hamper.webp', 'Kids Jute Party Hamper', 'Kids Hampers', 'A clear-window jute bag with stationery, snacks and toys, printed with the child\'s name.', 20, ['birthday']),
]
COLLEGE = [
    ('Gift set (7)-400x415.webp', 'Bottle, Notebook & Pen Gift Set', 'Gift Sets', 'Black steel bottle, cork-trim notebook and pen in a gift box, all logo-ready.', 25, ['employee-welcome', 'corporate']),
    ('PBGC217-bambox-travel-cable-box-universal-connectors-400x415.webp', 'Bamboo Travel Cable Organiser', 'Tech', 'A bamboo pod holding a universal charging cable with every connector. Laser-engrave your logo on the lid.', 25, ['corporate', 'eco']),
    ('PID3139-beautiful-magnet-roller-pens-400x415.webp', 'Carbon Roller Pen', 'Pens', 'A carbon-pattern roller pen with a magnetic cap and metal trim. Engraved with a name or logo.', 50, ['corporate']),
    ('Untitled-3-700x700.webp', 'Fast-Charge Power Bank with Cable', 'Tech', 'A slim power bank with a built-in cable and digital display. UV-print your logo on the face.', 25, ['corporate']),
    ('WhatsApp-Image-2024-06-20-at-3.57.12-PM.webp', 'Desk Phone Stand', 'Tech', 'A foldable desk stand for phones and tablets, with logo print on the base.', 50, ['corporate']),
    ('airclips-purple-500x500.webp', 'Open-Ear Wireless Earbuds', 'Tech', 'Clip-style open-ear wireless earbuds with a charging case. A premium freshers or fest prize.', 10, ['for-her', 'for-him']),
    ('artistix-agiespack-laptop-backpack-with-logo-front-400x415.webp', 'Logo Laptop Backpack', 'Bags', 'A clean black laptop backpack with a padded sleeve, printed or embroidered with your club or college logo.', 25, ['employee-welcome']),
    ('axis-personalized-roller-metal-pen-with-company-logo-min-400x415.webp', 'Gold-Trim Roller Pen', 'Pens', 'A black and gold metal roller pen, laser-engraved for convocations and placement drives.', 50, ['corporate']),
    ('buddy-lock-executive-stainless-steel-lunch-box-new-400x415.webp', 'Steel Lunch Box with Insulated Bag', 'Lunch & Bottles', 'Two leak-proof steel containers in an insulated zip bag with your logo.', 25, ['employee-welcome']),
    ('colour-changing-led-sports-hoop-245-xl.jpg', 'LED Mini Basketball Hoop', 'Fun & Decor', 'A colour-changing LED door hoop for hostel rooms. A fun fest or sports-meet prize.', 10, ['birthday']),
    ('customized-rechargeable-led-lamp-with-clip-on-base-400x415.webp', 'Clip-On LED Desk Lamp', 'Desk', 'A rechargeable clip-on reading lamp with a logo print on the clamp. Great for hostels.', 25, ['corporate']),
    ('digilife-desky-multifunctional-lamp-400x415.webp', 'Desk Lamp with Pen Stand', 'Desk', 'An LED lamp with a built-in pen stand and phone slot, printed with your brand.', 25, ['corporate']),
    ('elegant-power-bank-400x415.webp', '10000 mAh Power Bank', 'Tech', 'A slim 10000 mAh power bank with a full-colour UV logo print.', 25, ['corporate']),
    ('elite-premium-microwave-safe-lunch-box-new-400x415.webp', 'Lunch Kit with Bottle & Bag', 'Lunch & Bottles', 'Microwave-safe lunch boxes, a steel bottle and cutlery in a padded bag with your logo.', 25, ['employee-welcome']),
    ('executive-microwave-safe-lunch-box-set-red-new-400x415.webp', '3-Tier Steel Lunch Box with Bag', 'Lunch & Bottles', 'Three steel tiffins in a printed insulated carrier. A hit with hostellers and staff.', 25, ['employee-welcome']),
    ('personalized-see-thru-table-clock-400x415.webp', 'Digital Desk Clock with Temperature', 'Desk', 'A see-through digital clock with date and temperature, printed with your logo.', 50, ['corporate']),
    ('six-in-one-personalized-premium-shaving-kit-500x500.webp', 'Grooming Gift Kit', 'Gift Sets', 'Shaving cream, pre-shave scrub, balm and towel in a premium box. A farewell favourite.', 10, ['for-him', 'farewell']),
]
NEW_CATS = [
    {'slug': 'school-gifts', 'name': 'School Gifts', 'blurb': "Children's Day, annual day, return gifts and stationery kits for whole classes.", 'subcategories': ['Stationery Kits', 'Return Gifts', 'Kids Hampers', 'Mugs & Keepsakes', 'Bags & Bottles']},
    {'slug': 'college-gifts', 'name': 'College Gifts', 'blurb': 'Freshers kits, fest prizes, tech and hostel essentials, branded for your college or club.', 'subcategories': ['Tech', 'Lunch & Bottles', 'Desk', 'Pens', 'Bags', 'Gift Sets', 'Fun & Decor']},
]


def new_products():
    out = []
    for cat, rows, folder, pre in (('school-gifts', SCHOOL, 'school', 'SCH'), ('college-gifts', COLLEGE, 'college', 'CLG')):
        for i, (f, name, sub, desc, moq, occ) in enumerate(rows, 1):
            slug = __import__('re').sub(r'[^a-z0-9]+', '-', name.lower()).strip('-') + f'-{pre.lower()}-{i:02d}'
            out.append({'id': f'{pre}{i:02d}', 'slug': slug, 'name': name, 'category': cat, 'subcategory': sub, 'description': desc, 'moq': moq,
                        'sku': f'{pre}-{i:02d}', 'occasions': occ, 'features': [], 'branding': ['Name or logo print', 'Custom message tag'],
                        'bulkNote': f'Minimum {moq} pcs · branding included' if moq > 1 else 'Bulk pack', 'inStock': True, 'newArrival': True,
                        'bestseller': False, 'featured': False, 'sameDay': True, 'createdAt': STAMP, '_src': os.path.join(EX, folder, f), 'images': []})
    return out


# ---------------------------------------------------------------- events
# tags: a subcategory name, or "cat:<category slug>"
E = lambda name, blurb, tags, kit: {'name': name, 'blurb': blurb, 'tags': tags, 'kit': kit}
EVENTS = [
    {'slug': 'school', 'name': 'School', 'emoji': '🎒', 'color': 'bg-butter text-onpop', 'tagline': 'From Children\'s Day return gifts to Class 12 farewells.',
     'print': ['Name-printed stationery', 'Certificates & yearbooks', 'House-colour T-shirts', 'Medals & trophies'],
     'events': [
         E('Annual day', 'Prizes, chief-guest mementos and take-home kits for performers.', ['cat:school-gifts', 'Classic Notebooks', 'Bottles', 'Metal Keychains'], ['Memento', 'Notebook', 'Bottle', 'Certificate']),
         E('Sports day', 'Bottles, caps and medals that survive a full day outdoors.', ['Bottles', 'cat:school-gifts', 'Backpacks', 'Carabiner Hooks'], ['Sipper', 'Medal', 'House tee', 'Cap']),
         E("Teachers' Day", 'Thoughtful, useful gifts the staff room will actually use.', ['Diary & Pen Gift Sets', 'Mugs', 'Executive Notebooks', 'Card Holders'], ['Diary & pen', 'Mug', 'Thank-you card']),
         E("Children's Day", 'Stationery kits, totes and treats for every child in class.', ['cat:school-gifts'], ['Stationery kit', 'Tote', 'Treat', 'Name tag']),
         E('Class 12 farewell', 'Keepsakes the batch will hold on to after school.', ['Premium Collection', 'Metal Keychains', 'Diary & Pen Gift Sets', 'Bottles'], ['Yearbook', 'Keychain', 'Diary', 'Batch tee']),
         E('Science & art fair', 'Participant kits, judge gifts and winner prizes.', ['cat:school-gifts', 'Classic Notebooks', 'Tumblers'], ['Participant kit', 'Winner prize', 'Judge gift'])]},
    {'slug': 'college', 'name': 'College', 'emoji': '🎓', 'color': 'bg-lilac text-onpop', 'tagline': 'Fests, freshers, hackathons and placement season, sorted overnight.',
     'print': ['Fest tees & hoodies', 'Lanyards & ID passes', 'Stickers & posters', 'Club merch'],
     'events': [
         E('Fest & cultural night', 'Volunteer merch, artist gifts and competition prizes.', ['cat:college-gifts', 'Metal Keychains', 'Bottles', 'Sling Bags'], ['Fest tee', 'Lanyard', 'Bottle', 'Prize']),
         E('Freshers', 'Welcome kits that make the first week feel easy.', ['cat:college-gifts', 'Backpacks', 'Classic Notebooks', 'Bottles'], ['Backpack', 'Notebook', 'Bottle', 'ID lanyard']),
         E('Hackathon', 'Participant swag, mentor gifts and winner hampers.', ['cat:college-gifts', 'Laptop & Messenger Bags', 'Tumblers', 'Executive Notebooks'], ['Tee', 'Tumbler', 'Stickers', 'Power bank']),
         E('Placement drive', 'Polished gifts for recruiters and panel members.', ['Diary & Pen Gift Sets', 'Card Holders', 'cat:college-gifts', 'Laptop & Messenger Bags'], ['Diary & pen', 'Card holder', 'Bottle']),
         E('Alumni meet', 'Branded keepsakes with a bit of nostalgia.', ['Premium Collection', 'Mugs', 'Diary & Pen Gift Sets', 'Leather & Cork'], ['Mug', 'Keychain', 'Diary']),
         E('Club events', 'Merch and prizes for clubs and societies, small runs welcome.', ['Metal Keychains', 'cat:college-gifts', 'Bottles', 'Classic Notebooks'], ['Club tee', 'Badge', 'Keychain'])]},
    {'slug': 'university', 'name': 'University', 'emoji': '🏛️', 'color': 'bg-ink text-paper', 'tagline': 'Convocations, conferences and symposiums with a premium finish.',
     'print': ['Delegate kits & folders', 'Conference badges', 'Banners & standees', 'Engraved mementos'],
     'events': [
         E('Convocation', 'Graduate keepsakes and chief-guest gifts.', ['Premium Collection', 'Diary & Pen Gift Sets', 'Card Holders', 'Leather & Cork'], ['Memento', 'Pen', 'Certificate folder']),
         E('Conferences & seminars', 'Delegate kits that look the part.', ['Executive Notebooks', 'Laptop & Messenger Bags', 'Bottles', 'Diary & Pen Gift Sets'], ['Conference bag', 'Notebook', 'Pen', 'Badge']),
         E('Faculty development programme', 'Practical desk gifts for participants.', ['Diary & Pen Gift Sets', 'Executive Notebooks', 'Tumblers', 'cat:college-gifts'], ['Diary', 'Tumbler', 'Pen']),
         E('Research symposium', 'Speaker gifts and presenter kits.', ['Executive Notebooks', 'cat:college-gifts', 'Bottles', 'Card Holders'], ['Notebook', 'Bottle', 'Memento']),
         E('Guest lectures', 'A respectful thank-you for visiting speakers.', ['Diary & Pen Gift Sets', 'Corporate Gift Hampers', 'Card Holders', 'Mugs'], ['Gift set', 'Shawl or hamper', 'Card']),
         E('Sports meet', 'Team kits, bottles and podium prizes.', ['Bottles', 'Backpacks', 'Carabiner Hooks', 'Sling Bags'], ['Team tee', 'Bottle', 'Medal'])]},
    {'slug': 'office', 'name': 'Office', 'emoji': '💼', 'color': 'bg-coral text-white', 'tagline': 'Joining kits, farewells and client gifts, ready for tomorrow.',
     'print': ['Welcome cards', 'Branded tees & hoodies', 'ID cards & lanyards', 'Standees & backdrops'],
     'events': [
         E('New joiner', 'A day-one kit that says "glad you\'re here".', ['Diary & Pen Gift Sets', 'Bottles', 'Backpacks', 'Mugs', 'Metal Keychains'], ['Diary & pen', 'Bottle', 'Backpack', 'Welcome card']),
         E('Farewell', 'A proper send-off with a personal touch.', ['Premium Collection', 'Laptop & Messenger Bags', 'Card Holders', 'Tumblers'], ['Laptop bag', 'Engraved pen', 'Card']),
         E('Town hall & annual day', 'Gifts for the whole floor, delivered together.', ['Tumblers', 'Executive Notebooks', 'Metal Keychains', 'Bottles'], ['Tumbler', 'Notebook', 'Tee']),
         E('Offsite', 'Travel-ready kits for the team trip.', ['Backpacks', 'Sling Bags', 'Bottles', 'Carabiner Hooks'], ['Backpack', 'Bottle', 'Cap', 'Tee']),
         E('Client visit', 'A desk-worthy gift for important guests.', ['Corporate Gift Hampers', 'Diary & Pen Gift Sets', 'Card Holders', 'Drinkware Sets'], ['Gift box', 'Card holder', 'Diary']),
         E('Work anniversary', 'Milestone gifts engraved with name and years.', ['Premium Collection', 'Leather & Cork', 'Tumblers', 'Laptop & Messenger Bags'], ['Engraved gift', 'Card', 'Hamper'])]},
    {'slug': 'govt-official', 'name': 'Govt & official', 'emoji': '🇮🇳', 'color': 'bg-butter text-onpop', 'tagline': 'Dignified gifts for inaugurations, delegations and national days, with GST invoices.',
     'print': ['Engraved plaques', 'Delegate folders', 'Awareness tees & caps', 'Banners & flags'],
     'events': [
         E('Inaugurations', 'Memorable gifts for chief guests and dignitaries.', ['Corporate Gift Hampers', 'Diary & Pen Gift Sets', 'Serveware & Decor', 'Executive Notebooks'], ['Memento', 'Gift box', 'Shawl']),
         E('Seminars', 'Participant kits for government trainings.', ['Executive Notebooks', 'Laptop & Messenger Bags', 'Bottles', 'Diary & Pen Gift Sets'], ['Folder bag', 'Notebook', 'Pen']),
         E('Award ceremonies', 'Trophies, plaques and winner gifts.', ['Premium Collection', 'Card Holders', 'Diary & Pen Gift Sets', 'Serveware & Decor'], ['Trophy', 'Certificate', 'Gift set']),
         E('Independence & Republic Day', 'Tricolour giveaways for staff and students.', ['Bottles', 'Metal Keychains', 'Classic Notebooks', 'Mugs'], ['Flag badge', 'Mug', 'Sweets']),
         E('Delegations', 'Premium gifts that represent your department well.', ['Corporate Gift Hampers', 'Drinkware Sets', 'Serveware & Decor', 'Premium Collection'], ['Copper set', 'Decor', 'Hamper']),
         E('Awareness drives', 'High-volume giveaways at the right budget.', ['Bottles', 'Sling Bags', 'Classic Notebooks', 'Carabiner Hooks'], ['Cap', 'Tee', 'Bottle', 'Tote'])]},
    {'slug': 'festivals', 'name': 'Festivals', 'emoji': '🪔', 'color': 'bg-coral text-white', 'tagline': 'Festive hampers for teams, clients and family, every season.',
     'print': ['Printed greeting cards', 'Branded sleeves & boxes', 'Name tags', 'Custom ribbons'],
     'events': [
         E('Diwali', 'Hampers, copper sets and decor with your branding.', ['Gift Hampers', 'Corporate Gift Hampers', 'Home Decor', 'Sweets & Dry Fruits'], ['Hamper', 'Diya set', 'Dry fruits']),
         E('New Year', 'Planners, diaries and desk gifts to start the year.', ['Executive Notebooks', 'Tumblers', 'Diary & Pen Gift Sets', 'Mugs'], ['Diary', 'Calendar', 'Tumbler']),
         E('Raksha Bandhan', 'Sweet boxes and gifts for sisters and brothers on the team.', ['Sweets & Dry Fruits', 'Gift Hampers', 'Card Holders', 'Bottles'], ['Sweets', 'Rakhi', 'Gift']),
         E('Navratri & Durga Puja', 'Festive decor, pooja items and sweets.', ['Home Decor', 'Sweets & Dry Fruits', 'Kitchen & Dining', 'Gift Hampers'], ['Decor', 'Sweets', 'Pooja thali']),
         E('Holi', 'Colourful hampers and treats for the celebration.', ['Sweets & Dry Fruits', 'Mugs', 'Gift Hampers', 'Bottles'], ['Gulal pack', 'Sweets', 'Tee']),
         E('Christmas & Eid', 'Season\'s gifts, from kids\' stationery to festive hampers.', ['cat:school-gifts', 'Gift Hampers', 'Mugs', 'Sweets & Dry Fruits'], ['Hamper', 'Mug', 'Treats'])]},
    {'slug': 'concerts', 'name': 'Concerts', 'emoji': '🎤', 'color': 'bg-ink text-paper', 'tagline': 'Passes, merch and green-room gifts, printed overnight.',
     'print': ['Artist & crew passes', 'Merch tees & hoodies', 'Tickets & posters', 'Wristbands & lanyards'],
     'events': [
         E('Artist & crew passes', 'Laminated passes, lanyards and access tags.', ['Metal Keychains', 'Leather & Cork', 'Carabiner Hooks', 'Card Holders'], ['Pass', 'Lanyard', 'Badge holder']),
         E('Merch', 'Sell-out merch: bottles, totes, keychains and more.', ['Bottles', 'Tumblers', 'Sling Bags', 'Metal Keychains'], ['Tee', 'Tote', 'Keychain', 'Bottle']),
         E('VIP & green room', 'Welcome hampers for artists and VIP guests.', ['Gift Hampers', 'Drinkware Sets', 'Tumblers', 'Premium Collection'], ['Hamper', 'Tumbler', 'Card']),
         E('Staff tees', 'Crew and volunteer tees with bottles and caps.', ['Bottles', 'Carabiner Hooks', 'Sling Bags'], ['Crew tee', 'Cap', 'Bottle']),
         E('Tickets & posters', 'Offset-printed tickets, posters and flyers.', ['Metal Keychains', 'Classic Notebooks', 'Mugs'], ['Tickets', 'Posters', 'Flyers']),
         E('Sponsor activations', 'Branded giveaways for sponsor booths.', ['Tumblers', 'Bottles', 'Metal Keychains', 'Backpacks'], ['Giveaway', 'Tote', 'Sticker'])]},
    {'slug': 'live-other', 'name': 'Live & other', 'emoji': '✨', 'color': 'bg-lilac text-onpop', 'tagline': 'Weddings, launches, expos, marathons and more.',
     'print': ['Wedding favour tags', 'Expo standees', 'Race bibs & tees', 'Custom packaging'],
     'events': [
         E('Weddings', 'Guest favours, room hampers and family gifts.', ['Gift Hampers', 'Home Decor', 'Sweets & Dry Fruits', 'Drinkware Sets'], ['Favour box', 'Hamper', 'Decor']),
         E('Product launches', 'Press kits and influencer boxes.', ['Corporate Gift Hampers', 'Tumblers', 'Executive Notebooks', 'Backpacks'], ['PR box', 'Tumbler', 'Notebook']),
         E('Expos', 'Booth giveaways that people keep.', ['Metal Keychains', 'Bottles', 'Classic Notebooks', 'Sling Bags'], ['Keychain', 'Tote', 'Notebook']),
         E('Marathons', 'Runner kits: bottles, bags and finisher gifts.', ['Bottles', 'Carabiner Hooks', 'Sling Bags', 'Backpacks'], ['Bib', 'Tee', 'Bottle', 'Medal']),
         E('Satsang & religious events', 'Prasad boxes, pooja gifts and sevadar kits.', ['Home Decor', 'Serveware & Decor', 'Sweets & Dry Fruits', 'Classic Notebooks'], ['Prasad box', 'Diya', 'Diary']),
         E('Birthdays', 'Return gifts and personalised presents.', ['cat:school-gifts', 'Mugs', 'Gift Hampers', 'Metal Keychains'], ['Return gift', 'Mug', 'Hamper'])]},
]
