module rdma_parser(
input  wire clk,
input  wire rst,

//Input AXI Stream Interface
input  wire [63   : 0]    data_slave,
input  wire [7    : 0]    keep_slave,
input  wire [0    : 0]    valid_slave,
input  wire [0    : 0]    last_slave,
output wire [0    : 0]    ready_slave,

//Output AXI Stream Interface
output wire [63   : 0]    data_master,
output wire [7    : 0]    keep_master,
output wire [0    : 0]    valid_master,
output wire [0    : 0]    last_master,
input  wire [0    : 0]    ready_master,

//Output results
output reg  [15   : 0]    src_port,
output reg  [15   : 0]    dst_address,
output reg  [15   : 0]    length,
output reg  [15   : 0]    checksum
);

localparam IDLE = 4'b0001,
               HEAD = 4'b0010,
               DATA = 4'b0100,
               WAIT = 4'b1000;
    
    reg [3:0] ps;
    reg [3:0] ns;
    
    wire is_idle;
    wire is_head;
    wire is_data;
    wire is_wait; 
    
    assign is_idle = (ps == IDLE);
    assign is_head = (ps == HEAD);
    assign is_data = (ps == DATA);
    assign is_wait = (ps == WAIT);

wire [63  :0] data_out;
    reg  [7   :0] keep_out;
    wire [0   :0] valid_out;
    wire [0   :0] last_out;
    wire [0   :0] ready_out;

reg  [63  :0] data;
    reg  [0   :0] valid;
    reg  [0   :0] last;
reg  [15  :0] length;
reg  [3   :0] header;
wire [63  :0] rdata;

assign data_out = data[63:0];

    assign valid_out = (is_data & valid) | last;
    assign last_out  = (length <= 'd8  ) & valid_out;
    assign ready_slave = ready_out & ~last;
    

    assign data_master  = data_out;
    assign valid_master = valid_out;
    assign keep_master  = keep_out;
    assign last_master  = last_out;
    assign ready_out    = ready_master;
    always @ (*)
    begin 
        keep_out = 0;
        case (length)
        'd7  : keep_out =   8'h7f;
        'd6  : keep_out =   8'h3f;
        'd5  : keep_out =   8'h1f;
        'd4  : keep_out =   8'h0f;
        'd3  : keep_out =   8'h07;
        'd2  : keep_out =   8'h03;
        'd1  : keep_out =   8'h01;
        'd0  : keep_out =   8'h00;
        default: keep_out =   8'hff;
        endcase
    end
    
assign rdata = {
data[7   :   0],
data[15  :   8],
data[23  :  16],
data[31  :  24],
data[39  :  32],
data[47  :  40],
data[55  :  48],
data[63  :  56]
};

wire valid_ready;
    assign valid_ready = valid_slave & ready_slave;
    
    wire true_last;
    assign true_last = last_slave & valid_ready;
    
wire header_last;
    assign header_last = (header == 'd0);

always @(posedge clk or posedge rst) 
    begin
        if (rst) ps <= IDLE;
        else     ps <= ns;
    end

always @ (*)
    begin
        case (ps)
            IDLE:   if  (valid_ready)   ns = HEAD;
                    else                ns = IDLE;
            HEAD:   if  (valid_ready & header_last)
                                        ns = DATA;
                    else                ns = HEAD;
            DATA:   if (last_out & ready_master) 
                    begin
                        if (last)       ns = IDLE;
                        else            ns = WAIT;
                    end
                    else                ns = DATA;
            WAIT:   if (true_last)      ns = IDLE;
                    else                ns = WAIT;
            default:                    ns = IDLE;
        endcase
    end

always @ (posedge clk)
    begin 
        if (valid_ready) begin
            data <= data_slave;
        end
        else begin
            data <= data;
        end
    end
    
    always @ (posedge clk or posedge rst) 
    begin
        if (rst)
            valid <= 'b0;
        else if (ready_master)
            valid <= valid_ready;
        else
            valid <= valid;
    end
    
    always @ (posedge clk or posedge rst)
    begin
        if (rst)
            last <= 1'b0;
        else if (true_last)
            last <= 1'b1;
        else if (ns == IDLE)
            last <= 1'b0;
        else
            last <= last;
    end
    
    always @ (posedge clk or posedge rst)
    begin
        if (rst)
        begin
        src_port <= 'd0;
        dst_address <= 'd0;
        length <= 'd0;
        checksum <= 'd0;
        end
        else if (is_head)
            case (header)
                'd0   : 
                begin
                    src_port[15:0] <= rdata[63:48];
                    dst_address[15:0] <= rdata[47:32];
                    length[15:0] <= rdata[31:16];
                    checksum[15:0] <= rdata[15:0];
                end
            endcase
        else
        begin
        src_port <= src_port;
        dst_address <= dst_address;
        length <= length;
        checksum <= checksum;
        end
    end

always @ (posedge clk or posedge rst)
    begin
        if (rst) 
            length <= 'd0;
        else if (is_head & (header == 'd0))
            length[15:0] <= rdata[31:16];
        else if (valid_out & ready_master)
            length <= length - 'd8;
        else if (ns == IDLE) 
            length <= 'd0;
        else 
            length <= length;
    end

always @(posedge clk or posedge rst) begin
        if (rst) 
            header <= 'd0;
        else if (~is_head)
            header <= 'd0;
        else if (valid_ready)
            header <= header + 'd1;
        else
            header <= header;
    end
    
    endmodule